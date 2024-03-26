import re

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


def traverse_graph(sourceList: list[str]):
    for file in sourceList:
        wiki_links = read_markdown_file(file)
        for link in wiki_links:
            print(link)
            # print(alias)
