import re
import frontmatter
from datetime import datetime
import os


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


def change_front_matter(post: frontmatter.Post, allowed_keys: set[str]) -> None:
    if "title" not in post.metadata:
        raise ValueError("Title is missing in front matter.")

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


# Function to convert wiki link to Hugo format
def convert_to_hugo_format(match: re.Match) -> str:
    link = match.group(1).strip()
    alias = match.group(3) if match.group(2) else link

    link = slugify_filename(link)

    if link.lower().endswith(".excalidraw"):
        link = re.sub(r"\.excalidraw$", ".excalidraw.svg", link, flags=re.IGNORECASE)

    if re.search(r"\.(png|jpg|jpeg|gif|svg|webp)$", link, re.IGNORECASE):
        # Format the markdown for an image
        return "[{}]({})".format(alias, "/blog/notes/images/" + link)

    hugo_link = link + ".md"
    # Replace with your actual Hugo shortcode format for links.
    # Here I'm assuming a hypothetical Hugo shortcode for links like: {{< link "url" "text" >}}
    return '[{}]({{{{< relref "{}" >}}}})'.format(alias, hugo_link)


def convert_file_to_hugo_format(
    input_file_path: str, output_file_path: str, allowed_keys: set[str] = set()
) -> None:
    post = frontmatter.load(input_file_path)
    change_front_matter(post, allowed_keys)

    content = post.content
    new_content = wiki_link_pattern.sub(convert_to_hugo_format, content)
    post.content = new_content
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        # Manually serialize the front matter and content
        front_matter_str = frontmatter.dumps(post)
        output_file.write(front_matter_str)


def slugify_filename(input_filename: str) -> str:
    # Separate the base of the filename from the extension
    input_filename = input_filename.lower()
    filename_base, file_extension = os.path.splitext(input_filename)
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
        print(f"Processing {link}")
        file_path = file_name_to_path_dict[link + ".md"]
        new_file_name = slugify_filename(link)
        new_file_name = new_file_name + ".md"
        new_path = os.path.join(notes_destination_dir, new_file_name)
        convert_file_to_hugo_format(file_path, new_path, allowed_keys)
