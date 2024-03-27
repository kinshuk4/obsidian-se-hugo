import logging
import os
import re
from collections import deque
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


# def traverse_graph(source_list: list[str], visited: set[str], file_dict: dict[str, str]):
#     reachable_links = set()
#     reachable_assets = set()
#     print("SOURCE LIST: ", source_list)
#     for file in source_list:
#         file_name = os.path.basename(file)
#         if (file_name in visited):
#             continue
#         visited.add(file_name)
#         reachable_links.add(file_name)
#         outgoing_links = read_markdown_file(file)
#         for (link, _) in outgoing_links:
#             has_ext = has_extension(link)
#             print("link: %s, has_ext: %b", link, has_ext)
#             if has_ext:
#                 reachable_assets.add(link)
#             else:
#                 reachable_links.add(link)
#                 markdown_link = link + ".md"
#                 (more_reachable_links, more_reachable_assets) = traverse_graph([file_dict[markdown_link]], visited.copy(), file_dict)
#                 reachable_links |= more_reachable_links
#                 reachable_assets |= more_reachable_assets
    
#     logging.info("REACHABLE LINKS: %s", reachable_links)
#     logging.info("REACHABLE ASSETS: %s", reachable_assets)
#     return reachable_links, reachable_assets

def traverse_graph(source_list: list[str], file_dict: dict[str, str]):
    bfs(source_list, file_dict)
    
def bfs(source_list: list[str], file_dict: dict[str, str]):
    visited = set()
    reachable_links = set()
    reachable_assets = set()
    queue = deque(source_list)

    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            base_file_name = os.path.basename(node)
            base_file_name_wo_ext, _ = os.path.splitext(base_file_name)
            reachable_links.add(base_file_name_wo_ext)
            outgoing_links = read_markdown_file(node)
            neighbors = []
            for (link, _) in outgoing_links:
                has_ext = has_extension(link)
                if has_ext:
                    reachable_assets.add(link)
                else:
                    markdown_link = link + ".md"
                    neighbors.append(file_dict[markdown_link])
            # Process node if needed, then add its neighbors to the queue
            # Here we add to the queue all adjacent nodes that haven't been visited
            queue.extend(neighbor for neighbor in neighbors if neighbor not in visited)

    print("REACHABLE LINKS: ", reachable_links)
    print("REACHABLE ASSETS: ", reachable_assets)
    return reachable_links, reachable_assets