import os
import shutil
import sys
import logging
import subprocess
from pathlib import Path
from obsidian_se_hugo.hugo_util import slugify_filename
from obsidian_se_hugo.markdown_util import read_json_from_markdown

EXCALIDRAW_SUBDIR = "excalidraw"
REGULAR_IMAGES_SUBDIR = "regular"


def get_dir_path(directory_path: str):
    return Path(directory_path)


def get_dir_path_or_exit(
    pathStr: str, logger: logging.Logger = logging.getLogger(__name__)
):
    path = Path(pathStr)

    if not os.path.isdir(path):
        logger.info("Folder {pathStr} does not exist. Aborting!")
        sys.exit(1)

    return path


def delete_and_recreate_directory(
    directory: str, logger: logging.Logger = logging.getLogger(__name__)
):
    logger.info(f"Cleaning the folder: {directory}")
    post_destination = Path(directory)
    delete_target(post_destination, logger)
    create_directory_if_not_exists(post_destination, logger=logger)


def delete_target(
    destination_dir: str, logger: logging.Logger = logging.getLogger(__name__)
):
    logger.debug(f"Deleting folder: {destination_dir}")
    destination = Path(destination_dir)
    if os.path.isdir(destination):
        shutil.rmtree(destination)
    else:
        logger.warning("DESTINATION folder %s does not exist.", str(destination_dir))


def delete_file(file_path):
    os.remove(file_path)


def read_text_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        markdown_text = f.read()
    return markdown_text


def create_file_name_to_path_dictionary(directory: str) -> dict[str, Path]:
    """
    Creates a dictionary with filenames as keys and their full paths as values.

    Args:
        directory: The starting directory to scan.

    Returns:
        A dictionary of filename to file path.
    """

    file_dict = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_dict[file] = file_path
    return file_dict


def has_extension(file_name):
    """Checks if a string has a file extension using regex.

    Args:
        file_string: The string to check for an extension.

    Returns:
        True if the string has an extension, False otherwise.
    """
    _, ext = os.path.splitext(file_name)
    return ext != ""


def create_directory_if_not_exists(dir_path: str, logger: logging.Logger = logging.getLogger(__name__)):
    logger.debug(f"Checking if directory exists: {dir_path}")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"Created directory: {dir_path}")


def copy_assets(
    asset_file_names: set[str],
    images_destination_dir: str,
    content_images_destination_dir: str,
    file_name_to_path_dict: dict[str, str],
):
    # Create subdirectories for different asset types
    excalidraw_dir = os.path.join(images_destination_dir, EXCALIDRAW_SUBDIR)
    regular_images_dir = os.path.join(images_destination_dir, REGULAR_IMAGES_SUBDIR)

    # Ensure that the destination directory exists
    os.makedirs(excalidraw_dir, exist_ok=True)
    os.makedirs(regular_images_dir, exist_ok=True)
    os.makedirs(content_images_destination_dir, exist_ok=True)

    image_dir = None
    # Copy each asset from the list to the destination directory
    for asset_filename in asset_file_names:
        base_filename = os.path.basename(asset_filename)
        if asset_filename.lower().endswith(".excalidraw"):
            # as excalidraw file has markdown extension at end
            # for now export to svg doesnt work properly, hence manually copying.
            asset_filename = asset_filename + ".md"
            base_filename = os.path.basename(asset_filename)
            image_dir = excalidraw_dir
        elif asset_filename.lower().endswith(".gif"):
            # as gif file has markdown extension at end
            # for now export to svg doesnt work properly, hence manually copying.
            image_dir = content_images_destination_dir
        else:
            image_dir = regular_images_dir

        source_path = file_name_to_path_dict[asset_filename]
        slugified_filename = slugify_filename(base_filename)
        destination_path = os.path.join(image_dir, slugified_filename)
        shutil.copy(source_path, destination_path)


def save_to_excalidraw_file(json_content, excalidraw_path):
    with open(excalidraw_path, "w", encoding="utf8") as file:
        file.write(json_content)


def convert_excalidraw_to_svg(excalidraw_path):
    # Placeholder for your actual conversion command
    command = ["excalidraw_export", excalidraw_path]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error: {result.stderr}")
        return False
    return True


def process_excalidraw_file_using_external_process(
    asset_filename: str,
    base_filename: str,
    images_destination_dir: str,
    file_name_to_path_dict: dict[str, str],
) -> bool:
    actual_asset_filename = asset_filename + ".md"
    source_path = file_name_to_path_dict[actual_asset_filename]
    svg_filename = os.path.splitext(base_filename)[0] + ".svg"
    slugified_svg_filename = slugify_filename(svg_filename)
    destination_path = os.path.join(images_destination_dir, slugified_svg_filename)
    result = extract_json_and_export_excalidraw_to_svg(source_path, destination_path)
    if not result:

        return False
    return True


def extract_json_and_export_excalidraw_to_svg(markdown_path, svg_path) -> bool:
    json_content = read_json_from_markdown(markdown_path)
    if json_content is not None:
        # create temp excalidraw file at same location where svg will be generated
        excalidraw_path = os.path.splitext(svg_path)[0] + ".excalidraw"
        save_to_excalidraw_file(json_content, excalidraw_path)
        if convert_excalidraw_to_svg(excalidraw_path):
            delete_file(excalidraw_path)
            return True
        else:
            return False
    else:
        logging.warning("No valid JSON content found in markdown file.")
        return False


def merge_folders(source_dir, dest_dir):
    """
    Merges files from source directory to destination directory,
    preserving folder structure and skipping existing files.

    Args:
      source_dir: Path to the source directory (manual-content).
      dest_dir: Path to the destination directory (content).
    """
    for root, dirs, files in os.walk(source_dir):
        # Construct relative path within destination directory
        relative_path = os.path.relpath(root, source_dir)
        dest_path = os.path.join(dest_dir, relative_path)

        # Create destination directory if it doesn't exist
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        for filename in files:
            if filename == ".DS_Store":
                continue
            source_file = os.path.join(root, filename)
            dest_file = os.path.join(dest_path, filename)

            # Skip existing files in destination
            if os.path.exists(dest_file):
                raise FileExistsError(
                    f"Destination File '{source_file}' already exists"
                )

            # Copy the file
            shutil.copy2(source_file, dest_file)
            logging.info(f"Copied: {source_file} to {dest_file}")
