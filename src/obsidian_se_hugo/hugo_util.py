import logging
import re
import frontmatter
from datetime import datetime
import os

from obsidian_se_hugo.markdown_util import get_hugo_section


default_allowed_frontmatter_keys_in_hugo = {
    "title",
    "draft",
    "date",
    "lastmod",
    "draft",
    "tags",
    "categories",
    "aliases",
}


def convert_date_to_iso(date_str: str) -> str:
    # Assuming the format is 'yyyy-mm-dd HH:MM' without seconds
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    # Converting to the ISO 8601 format with 'T' separator and 'Z' for UTC timezone
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def change_front_matter(post: frontmatter.Post, allowed_keys: set[str], input_file_path: str) -> None:
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

    # Remove extra keys from the markdown
    allowed_keys = allowed_keys.union(default_allowed_frontmatter_keys_in_hugo)
    post.metadata = {
        key: value for key, value in post.metadata.items() if key in allowed_keys
    }


wiki_link_pattern = re.compile(r"\[\[(.*?)(\|(.*?))?\]\]")
youtube_pattern = r"!\[(.*?)\]\((https:\/\/www\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)|https:\/\/youtu\.be\/([a-zA-Z0-9_-]+))\)"


def replace_wikilinks_with_markdown_links(content: str) -> str:
    # Function to convert wiki link to Hugo format
    def wikilink_to_markdown_replacer(match: re.Match) -> str:
        link = match.group(1).strip()
        alias = match.group(3) if match.group(2) else link

        link = slugify_filename(link)

        if link.lower().endswith(".excalidraw"):
            link = re.sub(
                r"\.excalidraw$", ".excalidraw.svg", link, flags=re.IGNORECASE
            )

        if re.search(r"\.(png|jpg|jpeg|gif|svg|webp)$", link, re.IGNORECASE):
            # Format the markdown for an image
            return "[{}]({})".format(alias, "/images/obsidian/" + link)

        hugo_link = link + ".md"
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


def convert_markdown_file_to_hugo_format(
    input_file_path: str, output_file_path: str, allowed_keys: set[str] = set()
) -> None:
    post = frontmatter.load(input_file_path)
    change_front_matter(post, allowed_keys, input_file_path)

    content = post.content
    # replace wikilinks with markdown links
    new_content = replace_wikilinks_with_markdown_links(content)
    # replace youtube links with hugo format
    new_content = replace_youtube_links_with_hugo_format_links(new_content)
    post.content = new_content
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        # Manually serialize the front matter and content
        front_matter_str = frontmatter.dumps(post)
        output_file.write(front_matter_str)


def slugify_filename(input_filename: str) -> str:
    # Separate the base of the filename from the extension
    input_filename = input_filename.lower()
    # to handle files with multiple dots eg. abc.excalidraw.md
    # find first dot file
    first_dot_index = input_filename.find(".")

    if first_dot_index != -1:
        filename_base = input_filename[:first_dot_index]
        file_extension = input_filename[first_dot_index:]
    else:
        filename_base = input_filename
        file_extension = ""

    # Replace spaces with hyphens, remove multiple hyphens, and remove any leftover invalid characters
    slugified = re.sub(r"\s+", "-", filename_base)
    slugified = re.sub(r"-+", "-", slugified)
    slugified = re.sub(r"[^\w\-]", "", slugified)
    # Return the slugified filename with the original file extension

    return slugified + file_extension


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
):
    for link in reachable_links:
        logging.info(f"Converting ({link}) to hugo format")
        file_path = file_name_to_path_dict[link + ".md"]
        new_file_name = slugify_filename(link)
        new_file_name = new_file_name + ".md"
        notes_destination_dir = get_hugo_section(file_path)
        new_path = os.path.join(hugo_content_dir, notes_destination_dir, new_file_name)
        convert_markdown_file_to_hugo_format(file_path, new_path, allowed_keys)