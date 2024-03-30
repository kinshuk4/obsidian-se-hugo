import re
import frontmatter


def convert_published_to_draft(post):
    post.metadata["draft"] = False
    if "published" in post.metadata:
        del post.metadata["published"]


wiki_link_pattern = re.compile(r"\[\[(.*?)(\|(.*?))?\]\]")


# Function to convert wiki link to Hugo format
def convert_to_hugo_format(match):
    link = match.group(1).strip()
    alias = match.group(3) if match.group(2) else link
    # Replace with your actual Hugo shortcode format for links.
    # Here I'm assuming a hypothetical Hugo shortcode for links like: {{< link "url" "text" >}}
    return '{{< link "{0}" "{1}" >}}'.format(link, alias)


def convert_file_to_hugo_format(input_file_path, output_file_path):
    post = frontmatter.load(input_file_path)
    convert_published_to_draft(post)
    print(post.metadata)

    content = post.content
    new_content = wiki_link_pattern.sub(convert_to_hugo_format, content)
    post.content = new_content
    # print(new_content)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Manually serialize the front matter and content
        front_matter_str = frontmatter.dumps(post)
        output_file.write(front_matter_str)


def convert_files_to_hugo_format(
    reachable_links, destination_str, destination_content_dir_str, file_to_dir_dict
):
    for link in reachable_links:
        print("Processing ", link)
        file_path = file_to_dir_dict[link + ".md"]
        new_path = (
            destination_str + "/" + destination_content_dir_str + "/" + link + ".md"
        )
        convert_file_to_hugo_format(file_path, new_path)
