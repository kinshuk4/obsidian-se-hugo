# Hierarchial path generated

import os
import logging
import sys
from pathlib import Path
from obsidian_se_hugo.config import load_config, Config
from obsidian_se_hugo.hugo_util import copy_markdown_files_using_hugo_section
from obsidian_se_hugo.markdown_util import get_alternate_link_dict, get_explicit_publish_list
from obsidian_se_hugo.file_util import (
    copy_assets,
    create_directory_if_not_exists,
    delete_target,
    merge_folders,
)
from obsidian_se_hugo.graph_util import grow_publish_list
from obsidian_se_hugo.file_util import create_file_name_to_path_dictionary


def configure_logging(log_level=logging.DEBUG):
    """Configures logging with a specified log level.

    Args:
        log_level (int, optional): The logging level. Defaults to logging.INFO.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler("logs/hierarchial-main.log", mode="a", encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def main():
    configure_logging()

    config: Config = load_config("conf/hconfig.yaml")

    logging.info("Successfully loaded configuration")

    obsidian_vault_path = Path(config.obsidian.root_path)
    if not os.path.isdir(obsidian_vault_path):
        logging.info("ORIGIN folder does not exist. Aborting!")
        sys.exit(1)

    hugo_site_path = Path(config.hugo.root_path)
    if not os.path.isdir(hugo_site_path):
        logging.info("Destination Parent folder does not exist. Aborting!")
        sys.exit(1)

    logging.info(f"ORIGIN: {obsidian_vault_path}, DESTINATION: {hugo_site_path}")

    hugo_content_path = os.path.join(config.hugo.root_path, config.hugo.content_dir)

    for posts_dir in config.hugo.posts_dir_list:
        logging.info(f"Cleaning the folder: {posts_dir}")
        posts_destination_dir = os.path.join(hugo_content_path, posts_dir)

        post_destination = Path(posts_destination_dir)

        print(f"DELETING target notes dir {post_destination}")
        delete_target(post_destination)
        print(f"Creating target notes dir {post_destination}")
        create_directory_if_not_exists(post_destination)

    images_destination_dir = os.path.join(config.hugo.root_path, config.hugo.images_dir)

    # Not useful as for me, images are under posts
    images_destination = Path(images_destination_dir)
    logging.info(f"DELETING images dir {post_destination}")
    delete_target(images_destination)

    images_content_destination_dir = os.path.join(config.hugo.root_path, config.hugo.content_images_dir)

    # Not useful as for me, images are under posts
    images_content_destination = Path(images_content_destination_dir)
    logging.info(f"DELETING images dir {images_content_destination}")
    delete_target(images_content_destination)

    initial_explicit_publish_list = get_explicit_publish_list(obsidian_vault_path)

    file_name_to_path_dict = create_file_name_to_path_dictionary(obsidian_vault_path)
    logging.info(f"File name to path dictionary: {len(file_name_to_path_dict)}")

    # {'Segment Tree Data Structure DS Index': 'https://en.wikipedia.org/wiki/Segment_tree'}
    file_name_to_alternate_link_dict = get_alternate_link_dict(obsidian_vault_path)
    print(file_name_to_alternate_link_dict)

    reachable_links, reachable_assets = grow_publish_list(
        initial_explicit_publish_list, file_name_to_path_dict
    )

    copy_markdown_files_using_hugo_section(
        reachable_links,
        hugo_content_path,
        file_name_to_path_dict,
        config.hugo.allowed_frontmatter_keys,
        file_name_to_alternate_link_dict,
    )

    copy_assets(reachable_assets, images_destination_dir, images_content_destination_dir, file_name_to_path_dict)
    hugo_manual_content_path = os.path.join(config.hugo.root_path, config.hugo.manual_content_dir)
    merge_folders(hugo_manual_content_path, hugo_content_path)


if __name__ == "__main__":
    main()
