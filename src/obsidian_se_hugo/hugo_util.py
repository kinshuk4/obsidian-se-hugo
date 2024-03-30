import re
import frontmatter
from datetime import datetime


def convert_date_to_iso(date_str):
    # Assuming the format is 'yyyy-mm-dd HH:MM' without seconds
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    # Converting to the ISO 8601 format with 'T' separator and 'Z' for UTC timezone
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def change_front_matter(post):
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


wiki_link_pattern = re.compile(r"\[\[(.*?)(\|(.*?))?\]\]")


# Function to convert wiki link to Hugo format
def convert_to_hugo_format(match):
    link = match.group(1).strip()
    if link.endswith("excalidraw"):
        # Do something if the link ends with "excalidraw"
        return
    alias = match.group(3) if match.group(2) else link
    hugo_link = slugify_filename(link) + ".md"
    # Replace with your actual Hugo shortcode format for links.
    # Here I'm assuming a hypothetical Hugo shortcode for links like: {{< link "url" "text" >}}
    return '[{}]({{{{< relref "{}" >}}}})'.format(alias, hugo_link)


def convert_file_to_hugo_format(input_file_path, output_file_path):
    post = frontmatter.load(input_file_path)
    change_front_matter(post)
    print(post.metadata)

    content = post.content
    new_content = wiki_link_pattern.sub(convert_to_hugo_format, content)
    post.content = new_content
    # print(new_content)
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        # Manually serialize the front matter and content
        front_matter_str = frontmatter.dumps(post)
        output_file.write(front_matter_str)

def slugify_filename(input_filename):
    slugified = input_filename.lower()
    slugified = re.sub(r'\.md$', '', slugified) 
    slugified = slugified.replace(" ", "-")
    # Remove or replace other non-URL-safe characters, as needed
    # This regex removes any characters that are not alphanumeric, hyphens, or periods
    slugified = re.sub(r'[^\w\.-]', '', slugified)
    return slugified


def convert_and_copy_files_to_hugo_format(
    reachable_links, destination_str, destination_content_dir_str, file_to_dir_dict
):
    for link in reachable_links:
        print("Processing ", link)
        file_path = file_to_dir_dict[link + ".md"]
        new_file_name = slugify_filename(link)
        new_path = (
            destination_str + "/" + destination_content_dir_str + "/" + new_file_name + ".md"
        )
        convert_file_to_hugo_format(file_path, new_path)


def copy_assets(
    reachable_assets, destination_str, destination_content_dir_str, file_to_dir_dict
):
    for link in reachable_assets:
        print("Processing ", link)
        file_path = file_to_dir_dict[link + ".md"]
        new_path = (
            destination_str + "/" + destination_content_dir_str + "/" + link + ".md"
        )
        convert_file_to_hugo_format(file_path, new_path)
