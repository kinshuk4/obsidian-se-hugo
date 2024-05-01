import logging
from pathlib import Path
import frontmatter
import re
from .hyperlink import Hyperlink


def should_publish_post_explicitly(file_path: str, publish_key: str = "published"):
    post = frontmatter.load(file_path)
    return post.get(publish_key, False)


def get_explicit_publish_list(
    origin: Path, publish_key: str = "published"
) -> list[str]:
    to_publish = []
    for file in origin.rglob("*.md"):
        if should_publish_post_explicitly(file, publish_key):
            logging.info("TO PUBLISH: %s", str(file))
            to_publish.append(str(file))
    return to_publish


wiki_link_pattern = r"\[\[(.+?)(\|.*?)?\]\]"


def extract_wiki_links(markdown_text: str) -> list[Hyperlink]:
    """
    This function extracts wiki links from a markdown file using regular expressions.

    Args:
        markdown_text: The text content of the markdown file as a string.

    Returns:
        A list of extracted wiki links as Hyperlink objects.
    """
    matches = re.findall(wiki_link_pattern, markdown_text)
    wiki_links = []
    for match in matches:
        # The first item is the link, the second is the alias which might be empty
        link = match[0]
        alias = match[1][1:] if match[1] else None  # Exclude the leading pipe character
        hyperlink = Hyperlink(link, alias)
        wiki_links.append(hyperlink)

    return wiki_links


# Read the markdown file and extract JSON content
def read_json_from_markdown(markdown_path: str) -> str:
    with open(markdown_path, "r", encoding="utf8") as file:
        content = file.read()
        # This regex assumes that your JSON is correctly formatted and indented
        matches = re.search(r"```json\n([\s\S]*?)\n```", content)
        if matches:
            return matches.group(1).strip()
    return None

def get_hugo_section(file_path: str) -> str:
    post = frontmatter.load(file_path)
    key = "hugo_section"
    if key not in post:
        raise ValueError(f"{key} not found in file: {file_path}")
    return post.get(key)
