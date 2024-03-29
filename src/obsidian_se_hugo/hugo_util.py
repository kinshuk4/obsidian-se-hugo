import re

wiki_link_pattern = re.compile(r"\[\[(.*?)(\|(.*?))?\]\]")


# Function to convert wiki link to Hugo format
def convert_to_hugo_format(match):
    link = match.group(1).strip()
    alias = match.group(3) if match.group(2) else link
    # Replace with your actual Hugo shortcode format for links.
    # Here I'm assuming a hypothetical Hugo shortcode for links like: {{< link "url" "text" >}}
    return '{{< link "{0}" "{1}" >}}'.format(link, alias)


def convert_file_to_hugo_format(input_file_path, output_file_path):
    with open(input_file_path, "r", encoding="utf-8") as input_file:
        content = input_file.read()

        # Replace all wiki links with Hugo format
        new_content = wiki_link_pattern.sub(convert_to_hugo_format, content)

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(new_content)
