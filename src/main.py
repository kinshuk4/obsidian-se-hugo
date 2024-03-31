import os
import logging
import sys
from pathlib import Path
from obsidian_se_hugo.config import load_config, Config, ObsidianConfig
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

    config: Config = load_config("conf/config.yaml")

    obsidian_vault_path = Path(config.obsidian.root_path)
    if not os.path.isdir(obsidian_vault_path):
        logging.debug("ORIGIN folder does not exist. Aborting!")
        sys.exit(1)

    hugo_site_path = Path(config.hugo.root_path)
    if not os.path.isdir(hugo_site_path):
        logging.debug("Destination Parent folder does not exist. Aborting!")
        sys.exit(1)

    logging.info(f"ORIGIN: {obsidian_vault_path}, DESTINATION: {hugo_site_path}")

    posts_destination_dir = os.path.join(config.hugo.root_path, config.hugo.posts_dir)
    images_destination_dir = os.path.join(config.hugo.root_path, config.hugo.images_dir)

    post_destination = Path(posts_destination_dir)

    logging.info(f"DELETING target notes dir {post_destination}")
    delete_target(post_destination)

    # Not useful as for me, images are under posts
    images_destination = Path(images_destination_dir)
    logging.info(f"DELETING target notes dir {post_destination}")
    delete_target(images_destination)

    create_directory_if_not_exists(posts_destination_dir)

    initial_explicit_publish_list = get_explicit_publish_list(obsidian_vault_path)

    file_name_to_path_dict = create_file_name_to_path_dictionary(obsidian_vault_path)
    logging.info(f"File name to path dictionary: {len(file_name_to_path_dict)}")

    reachable_links, reachable_assets = grow_publish_list(
        initial_explicit_publish_list, file_name_to_path_dict
    )

    copy_markdown_files_in_hugo_format(
        reachable_links,
        posts_destination_dir,
        file_name_to_path_dict,
        config.hugo.allowed_frontmatter_keys,
    )

    copy_assets(reachable_assets, images_destination_dir, file_name_to_path_dict)


if __name__ == "__main__":
    main()
