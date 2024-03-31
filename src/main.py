import os
import logging
import pathlib
import sys

from obsidian_se_hugo.hugo_util import copy_markdown_files_in_hugo_format
from obsidian_se_hugo.markdown_util import get_explicit_publish_list
from obsidian_se_hugo.file_util import (
    copy_assets,
    create_directory_if_not_exists,
    delete_target,
)
from obsidian_se_hugo.graph_util import grow_publish_list
from obsidian_se_hugo.file_util import create_file_name_to_path_dictionary


def configure_logging(log_level=logging.INFO):
    """Configures logging with a specified log level.

    Args:
        log_level (int, optional): The logging level. Defaults to logging.INFO.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler("logs/export-files.log", mode="w", encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def main():
    configure_logging()

    obsidian_vault_path_str = (
        "/Users/kinshuk.chandra/lyf/syncs/Dropbox/r00t/edu/Obsidian/apnotes-ob/r"
    )

    obsidian_vault_path = pathlib.Path(obsidian_vault_path_str)
    if not os.path.isdir(obsidian_vault_path):
        print("ORIGIN folder does not exist. Aborting!")
        sys.exit(1)

    hugo_site_path_str = "/Users/kinshuk.chandra/lyf/scm/github/k2/k5kc-site"
    hugo_site_path = pathlib.Path(hugo_site_path_str)
    if not os.path.isdir(hugo_site_path):
        print("Destination Parent folder does not exist. Aborting!")
        sys.exit(1)

    logging.info(
        f"ORIGIN: {obsidian_vault_path_str}, DESTINATION: {hugo_site_path_str}"
    )

    destination_notes_dir = "content/blog/notes"
    destination_images_dir = "content/blog/notes/images"

    notes_destination_dir = os.path.join(hugo_site_path_str, destination_notes_dir)
    images_destination_dir = os.path.join(hugo_site_path_str, destination_images_dir)

    destination = pathlib.Path(notes_destination_dir)

    logging.info("DELETING target folder %s", hugo_site_path_str)
    delete_target(destination)

    create_directory_if_not_exists(notes_destination_dir)

    initial_explicit_publish_list = get_explicit_publish_list(obsidian_vault_path)

    file_name_to_path_dict = create_file_name_to_path_dictionary(obsidian_vault_path)
    logging.info(f"File name to path dictionary: {len(file_name_to_path_dict)}")

    reachable_links, reachable_assets = grow_publish_list(
        initial_explicit_publish_list, file_name_to_path_dict
    )

    copy_markdown_files_in_hugo_format(
        reachable_links,
        notes_destination_dir,
        file_name_to_path_dict,
        set()
    )

    copy_assets(reachable_assets, images_destination_dir, file_name_to_path_dict)


if __name__ == "__main__":
    main()
