import os
import logging
import pathlib
import sys

from obsidian_se_hugo.markdown_util import get_markdown_files_to_publish
from obsidian_se_hugo.file_util import delete_target
from obsidian_se_hugo.outedge_processor import traverse_graph
from obsidian_se_hugo.file_util import create_file_dictionary
def main():
    pathlib.Path("logs").mkdir(parents=True, exist_ok=True)
    # Create logs/ dir if it does not exist
    logging.basicConfig(
        filename="logs/export-files.log",
        filemode="w",
        encoding="utf-8",
        level=logging.INFO,
    )

    # (origin_str, destination_str) = parse_args()
    origin_str = (
        "/Users/kinshuk.chandra/lyf/syncs/Dropbox/r00t/edu/Obsidian/apnotes-ob/r"
    )
    destination_str = "/Users/kinshuk.chandra/lyf/scm/github/k2/k5kc-site"
    destination_content_dir_str = "content/notes"
    destination_image_dir_str = "content/images/obs"

    origin = pathlib.Path(origin_str)
    destination = pathlib.Path(destination_str + "/" + destination_content_dir_str)

    logging.info("ORIGIN: %s , DESTINATION: %s", origin_str, destination_str)
    if not os.path.isdir(origin):
        print("ORIGIN folder does not exist. Aborting!")
        sys.exit(1)

    logging.info("DELETING target folder %s", destination_str)
    delete_target(destination)

    excluded_dirs = [".git"]
    to_be_published_list = get_markdown_files_to_publish(origin)

    file_to_dir_dict = create_file_dictionary(origin)
    logging.info("FILE TO DIR DICT: %d", len(file_to_dir_dict))

    traverse_graph(to_be_published_list, file_to_dir_dict)

    # logging.info("COPYING Obsidian vault to target folder %s", destination_str)
    # copy_source_to_target(origin, destination)

    # logging.info("CREATING _index.md files")
    # create_index_files(destination)
    # root_to_index(destination)

    # #logging.info ("PRUNING files with publish != True")
    # #prune_nopublish(destination)

    # logging.info("ADDING dates to frontmatter")
    # add_frontmatter_date(destination)


if __name__ == "__main__":
    main()
