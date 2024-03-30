import logging
import frontmatter
import re

def to_be_published(file):
    post = frontmatter.load(file)
    if "published" in post.keys():
        if post["published"] != True:
            return False
        else:
            return True

    logging.debug("File %s has no publish key in frontmatter", str(file))
    return False


def get_markdown_files_to_publish(origin):
    to_publish = []
    for file in origin.rglob("*.md"):
        if to_be_published(file):
            logging.info("TO PUBLISH: %s", str(file))
            to_publish.append(str(file))
    return to_publish


wiki_link_pattern = r"\[\[(.+?)(\|.*?)?\]\]"


def extract_wiki_links(markdown_text):
    """
    This function extracts wiki links from a markdown file using regular expressions.

    Args:
        markdown_text: The text content of the markdown file as a string.

    Returns:
        A list of extracted wiki links (strings).
    """
    # wiki_link_pattern = r"\[\[([^\|]+?)\|?([^\]]*)\]\]"  # Matches both [[wiki link]] and [[wiki link||alias]]

    matches = re.findall(wiki_link_pattern, markdown_text)
    wiki_links = []
    for match in matches:
        # The first item is the link, the second is the alias which might be empty
        link = match[0]
        alias = match[1][1:] if match[1] else None  # Exclude the leading pipe character
        wiki_links.append((link, alias))

    return wiki_links


# Read the markdown file and extract JSON content
def read_json_from_markdown(markdown_path):
    with open(markdown_path, 'r', encoding='utf8') as file:
        content = file.read()
        # This regex assumes that your JSON is correctly formatted and indented
        matches = re.search(r'```json\n([\s\S]*?)\n```', content)
        if matches:
            return matches.group(1).strip()
    return None
