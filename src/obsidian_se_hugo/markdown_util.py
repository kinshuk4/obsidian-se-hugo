import logging
from pathlib import Path
import frontmatter
import re
from .hyperlink import Hyperlink
import os
from obsidian_se_hugo.constants import (
    wiki_link_pattern,
    code_block_pattern,
    inline_code_pattern,
)


def is_published(file_path: str, publish_key: str = "published") -> bool:
    try:
        post = frontmatter.load(file_path)
        return post.get(publish_key, False)
    except Exception as e:
        logging.error(f"Error in reading file: {file_path} - {e}")
        raise e


def get_alternate_link(file_path: str, alternate_link_key: str = "alternate_link"):
    post = frontmatter.load(file_path)
    if alternate_link_key not in post:
        return None
    return post.get(alternate_link_key)


def get_explicit_publish_list(
    origin: Path, publish_key: str = "published"
) -> list[str]:
    to_publish = []
    for file in origin.rglob("*.md"):
        if is_published(file, publish_key):
            logging.info("TO PUBLISH: %s", str(file))
            to_publish.append(str(file))
    return sorted(to_publish)


def get_alternate_link_dict(origin: Path, publish_key: str = "published") -> list[str]:
    alternate_link = {}
    for file in origin.rglob("*.md"):
        post = frontmatter.load(file)
        if "alternate_link" in post:
            logging.info("Alternate link in: %s", str(file))
            base_file_name = os.path.basename(file)
            base_file_name_wo_ext, _ = os.path.splitext(base_file_name)
            logging.info("TO PUBLISH: %s", str(file))
            alternate_link[base_file_name_wo_ext] = post.get("alternate_link")
    return alternate_link


def extract_wiki_links(markdown_text: str) -> list[Hyperlink]:
    """
    This function extracts wiki links from a markdown file using regular expressions.

    Args:
        markdown_text: The text content of the markdown file as a string.

    Returns:
        A list of extracted wiki links as Hyperlink objects.
    """
    # Split the markdown text into non-code parts using code blocks as delimiters
    non_code_parts = re.split(code_block_pattern, markdown_text)

    wiki_links = []
    for part in non_code_parts:
        # Extract wiki links from each non-code part
        sub_parts = re.split(
            inline_code_pattern, part
        )  # Split based on inline code texts
        for sub_part in sub_parts:
            wiki_links += extract_wiki_links_from_text(sub_part)

    return wiki_links


def extract_wiki_links_from_text(text: str) -> list[Hyperlink]:
    matches = re.findall(wiki_link_pattern, text)
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
    if key not in post and "alternate_link" not in post:
        raise ValueError(f"{key} not found in file: {file_path}")
    elif key not in post:
        return None
    return post.get(key)


def extract_single_wiki_link(wiki_link: str) -> str:
    """
    Extract the target from a wiki link string like [[target|alias]] or [[target]]
    """
    m = re.match(r"\[\[(.*?)(\|.*?)?\]\]", wiki_link)
    if m:
        return m.group(1).split("|")[0].strip()
    return wiki_link.strip()
