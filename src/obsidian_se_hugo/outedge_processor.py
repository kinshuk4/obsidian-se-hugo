import logging
import os
import re

from .file_util import has_extension

wiki_link_pattern = r'\[\[(.+?)(\|.*?)?\]\]'


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


def read_markdown_file(file_path):
    with open(file_path, "r") as f:
        markdown_text = f.read()
    wiki_links = extract_wiki_links(markdown_text)
    return wiki_links


def traverse_graph(source_list: list[str], visited: set[str], file_dict: dict[str, str]):
    reachable_links = set()
    reachable_assets = set()
    print("SOURCE LIST: ", source_list)
    for file in source_list:
        file_name = os.path.basename(file)
        if (file_name in visited):
            continue
        visited.add(file_name)
        reachable_links.add(file_name)
        outgoing_links = read_markdown_file(file)
        for (link, _) in outgoing_links:
            has_ext = has_extension(file_name)
            print("link: %s, has_ext: %b", link, has_ext)
            if has_ext:
                reachable_assets.add(link)
            else:
                reachable_links.add(link)
                (more_reachable_links, more_reachable_assets) = traverse_graph([file_dict[link]], visited.copy(), file_dict)
                reachable_links |= more_reachable_links
                reachable_assets |= more_reachable_assets
    
    logging.info("REACHABLE LINKS: %d, REACHABLE ASSETS: %d", len(reachable_links), len(reachable_assets))
    return reachable_links, reachable_assets
        
            
