import logging
import os
import re
from collections import deque

from obsidian_se_hugo.markdown_util import extract_wiki_links
from .file_util import has_extension


def read_markdown_file(file_path):
    with open(file_path, "r") as f:
        markdown_text = f.read()
    wiki_links = extract_wiki_links(markdown_text)
    return wiki_links


def grow_publish_list(
    source_list: list[str], file_dict: dict[str, str]
) -> tuple[set[str], set[str]]:
    return bfs(source_list, file_dict)


def bfs(source_list: list[str], file_dict: dict[str, str]) -> tuple[set[str], set[str]]:
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
            for link, _ in outgoing_links:
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
