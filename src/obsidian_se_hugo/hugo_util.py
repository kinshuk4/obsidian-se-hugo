import logging
import re
import frontmatter
from datetime import datetime
import os

from obsidian_se_hugo.markdown_util import get_hugo_section
from obsidian_se_hugo.constants import code_block_pattern, inline_code_pattern

default_allowed_frontmatter_keys_in_hugo = {
    "title",
    "draft",
    "date",
    "lastmod",
    "draft",
    "tags",
    "categories",
    "aliases",
    "difficulty",
    "companies",
    "topic",
    "order",
    "video_ids",
    "subtopics",
}

topic_to_category = {
    "database": ["database", "sql", "pandas"],
}


def convert_date_to_iso(date_str: str) -> str:
    # Assuming the format is 'yyyy-mm-dd HH:MM' without seconds
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    # Converting to the ISO 8601 format with 'T' separator and 'Z' for UTC timezone
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def change_front_matter(
    post: frontmatter.Post, allowed_keys: set[str], input_file_path: str
) -> None:
    if "title" not in post.metadata:
        raise ValueError(f"Title is missing in front matter in {input_file_path}")

    post.metadata["draft"] = False
    if "published" in post.metadata:
        del post.metadata["published"]

    if "date_created" in post.metadata:
        post.metadata["date"] = convert_date_to_iso(post.metadata["date_created"])
        del post.metadata["date_created"]

    if "date_modified" in post.metadata:
        post.metadata["lastmod"] = convert_date_to_iso(post.metadata["date_modified"])
        del post.metadata["date_modified"]

    # Add categories based on topic
    if "topic" in post.metadata:
        topic = post.metadata["topic"]
        if topic in topic_to_category:
            post.metadata["categories"] = topic_to_category[topic]
        else:
            post.metadata["categories"] = [topic]

    # Remove extra keys from the markdown
    allowed_keys = allowed_keys.union(default_allowed_frontmatter_keys_in_hugo)
    post.metadata = {
        key: value for key, value in post.metadata.items() if key in allowed_keys
    }


wiki_link_pattern = re.compile(r"\[\[(.*?)(\|(.*?))?\]\]")
youtube_pattern = r"!\[(.*?)\]\((https:\/\/www\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)|https:\/\/youtu\.be\/([a-zA-Z0-9_-]+))\)"


def replace_wikilinks_with_markdown_links(
    content: str, file_name_to_alternate_link_dict: dict[str, str] = {}
) -> str:
    # Function to convert wiki link to Hugo format
    def is_inside_code_block(start_index: int, end_index: int, text: str) -> bool:
        """
        Checks if the given indices fall inside a code block or inline code.
        """
        for pattern in [code_block_pattern, inline_code_pattern]:
            for match in re.finditer(pattern, text):
                if match.start() <= start_index < match.end() or match.start() < end_index <= match.end():
                    return True
        return False
    
    def wikilink_to_markdown_replacer(match: re.Match) -> str:

        if is_inside_code_block(match.start(), match.end(), content):
            return match.group(0)  # Return the original text if within a code block
        link = match.group(1).strip()
        alias = match.group(3) if match.group(2) else link

        link_parts = link.split("#", 1)
        section = ""
        if len(link_parts) > 1:
            link = link_parts[0]
            section = link_parts[1]
        
        # handle non published links as external links
        if link in file_name_to_alternate_link_dict:
            print(link)
            external_link = file_name_to_alternate_link_dict[link]
            return f"[{alias}]({external_link})"
        
        link = slugify_filename(link)
        section_slug = slugify_section(section) if section else ""

        if section_slug:
            section_slug = "#" + section_slug

        if link.lower().endswith(".excalidraw"):
            link = re.sub(
                r"\.excalidraw$", ".excalidraw.png", link, flags=re.IGNORECASE
            )

        if re.search(r"\.(png|jpg|jpeg|gif|svg|webp)$", link, re.IGNORECASE):
            # Format the markdown for an image
            return "[{}]({})".format(alias, "/images/obsidian/" + link)

        if not link:
            # Handle links like [[#header]]
            hugo_link = f"{section_slug}"
        else:
            section_slug = "/" + section_slug if section_slug else ""
            hugo_link = f"{link}.md{section_slug}"
        # Replace with your actual Hugo shortcode format for links.
        # Here I'm assuming a hypothetical Hugo shortcode for links like: {{< link "url" "text" >}}
        return '[{}]({{{{< relref "{}" >}}}})'.format(alias, hugo_link)

    return wiki_link_pattern.sub(wikilink_to_markdown_replacer, content)


def replace_youtube_links_with_hugo_format_links(content: str) -> str:
    # Function to convert youtube link to Hugo format
    def youtube_to_markdown_replacer(match: re.Match) -> str:
        alias = match.group(1).strip()
        # Extract video id from either type of URL
        youtube_id = match.group(3) if match.group(3) is not None else match.group(4)
        youtube_id = youtube_id.strip()
        title_part = f' title="{alias}"' if alias else ""
        return f'{{{{< youtube id="{youtube_id}"{title_part} >}}}}'

    return re.sub(youtube_pattern, youtube_to_markdown_replacer, content)

def replace_latex_syntax(content: str) -> str:
    """
    Replace LaTeX expressions in the content by changing "\\" to "\\\".
    LaTeX expressions are found between $$ ... $$.
    """
    def latex_replacer(match: re.Match) -> str:
        latex_content = match.group(1)
        # Replace "\\" with "\\\"
        updated_latex_content = latex_content.replace("\\\\", "\\\\\\")
        updated_latex_content = re.sub(r"\\\$", r"\\\\$", updated_latex_content)
        updated_latex_content = re.sub(r"\\\#", r"\\\\#", updated_latex_content)
        updated_latex_content = updated_latex_content.replace("\\cellcolor", "\\colorbox")
        return f"$${updated_latex_content}$$"

    # Regex pattern to find LaTeX expressions between $$
    latex_pattern = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
    updated_content = re.sub(latex_pattern, latex_replacer, content)
    
    return updated_content

def convert_markdown_file_to_hugo_format(
    input_file_path: str,
    output_file_path: str,
    allowed_keys: set[str] = set(),
    file_name_to_alternate_link_dict: dict[str, str] = {},
) -> None:
    post = frontmatter.load(input_file_path)
    change_front_matter(post, allowed_keys, input_file_path)

    content = post.content
    # replace wikilinks with markdown links
    new_content = replace_wikilinks_with_markdown_links(
        content, file_name_to_alternate_link_dict
    )
    # replace youtube links with hugo format
    new_content = replace_youtube_links_with_hugo_format_links(new_content)
    new_content = replace_latex_syntax(new_content)
    post.content = new_content
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        # Manually serialize the front matter and content
        front_matter_str = frontmatter.dumps(post)
        output_file.write(front_matter_str)


def slugify_filename(input_filename: str) -> str:
    # Lowercase the filename
    input_filename = input_filename.lower()

    # Find the first dot in the filename to determine where the extension starts
    first_dot_index = input_filename.find(".")

    # Separate the filename from the extension
    if first_dot_index != -1:
        filename_base = input_filename[:first_dot_index]
        file_extension = input_filename[first_dot_index:]
    else:
        filename_base = input_filename
        file_extension = ""

    # Replace any sequence of non-alphanumeric characters (except hyphens) with a hyphen
    slugified = re.sub(r"[^a-z0-9]+", "-", filename_base)

    # Return the slugified filename with the extension preserved
    return slugified + file_extension


def slugify_section(input: str) -> str:
    output = input.lower()

    # Replace spaces with a single hyphen
    output = re.sub(r"\s+", "-", output)

    return output


def copy_markdown_files_in_hugo_format(
    reachable_links: set[str],
    notes_destination_dir: str,
    file_name_to_path_dict: dict[str, str],
    allowed_keys=set[str](),
):
    for link in reachable_links:
        logging.info(f"Converting ({link}) to hugo format")
        file_path = file_name_to_path_dict[link + ".md"]
        new_file_name = slugify_filename(link)
        new_file_name = new_file_name + ".md"
        new_path = os.path.join(notes_destination_dir, new_file_name)
        convert_markdown_file_to_hugo_format(file_path, new_path, allowed_keys)


def copy_markdown_files_using_hugo_section(
    reachable_links: set[str],
    hugo_content_dir: str,
    file_name_to_path_dict: dict[str, str],
    allowed_keys=set[str](),
    file_name_to_alternate_link_dict: dict[str, str] = {},
):
    for link in reachable_links:
        logging.info(f"Converting ({link}) to hugo format")
        file_path = file_name_to_path_dict[link + ".md"]
        new_file_name = slugify_filename(link)
        new_file_name = new_file_name + ".md"
        notes_destination_dir = get_hugo_section(file_path)
        if not notes_destination_dir:
            # non publishable links
            continue
        new_path = os.path.join(hugo_content_dir, notes_destination_dir, new_file_name)
        convert_markdown_file_to_hugo_format(file_path, new_path, allowed_keys, file_name_to_alternate_link_dict)
