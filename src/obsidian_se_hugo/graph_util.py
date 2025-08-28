import logging
import os
from collections import deque

from .hyperlink import Hyperlink
from .markdown_util import extract_wiki_links, get_alternate_link, is_published
from .file_util import has_extension, read_text_file


def get_outgoing_links(file_path: str) -> list[Hyperlink]:
    should_be_published = is_published(file_path)
    if not should_be_published and not get_alternate_link(file_path):
        raise ValueError(
            f"File {file_path} should not be published and has no alternate link."
        )
    elif not should_be_published:
        return []
    markdown_text = read_text_file(file_path)
    wiki_links = extract_wiki_links(markdown_text)
    return wiki_links


def grow_publish_list(
    initial_explicit_publish_list: list[str], file_name_to_path_dict: dict[str, str]
) -> tuple[set[str], set[str]]:
    return bfs(initial_explicit_publish_list, file_name_to_path_dict)


def bfs(
    source_list: list[str], file_name_to_path_dict: dict[str, str]
) -> tuple[list[str], list[str]]:
    visited = set[str]()
    reachable_links = set[str]()
    reachable_assets = set[str]()
    queue = deque[str](source_list)

    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            base_file_name = os.path.basename(node)
            base_file_name_wo_ext, _ = os.path.splitext(base_file_name)
            reachable_links.add(base_file_name_wo_ext)
            outgoing_links = get_outgoing_links(node)
            neighbors = []
            for hyperlink in outgoing_links:
                link = hyperlink.link
                has_ext = has_extension(link)
                if has_ext:
                    reachable_assets.add(link)
                else:
                    # handle the links that link to headers
                    link_parts = link.split("#", 1)
                    file_link = link_parts[0]
                    if not file_link:
                        # some files have links like [[#header]], we ignore them
                        continue
                    markdown_link = file_link + ".md"
                    if markdown_link not in file_name_to_path_dict:
                        raise ValueError(
                            f"Outgoing Link {markdown_link} in '{base_file_name}' cannot be found."
                        )
                    neighbors.append(file_name_to_path_dict[markdown_link])
            # Process node if needed, then add its neighbors to the queue
            # Here we add to the queue all adjacent nodes that haven't been visited
            queue.extend(neighbor for neighbor in neighbors if neighbor not in visited)

    logging.info("Reachable Links: ", reachable_links)
    logging.info("Reachable Assets: ", reachable_assets)
    return sorted(reachable_links), sorted(reachable_assets)
