import os
import shutil
import logging
import subprocess


def delete_target(destination):
    if os.path.isdir(destination):
        shutil.rmtree(destination)
    else:
        logging.warning("DESTINATION folder %s does not exist.", str(destination))


def create_file_dictionary(directory):
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


def create_directory_if_not_exists(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def copy_assets(asset_paths, destination_folder):
    # Ensure that the destination directory exists
    os.makedirs(destination_folder, exist_ok=True)

    # Copy each asset from the list to the destination directory
    for asset_path in asset_paths:
        filename = os.path.basename(asset_path)
        if asset_path.lower().endswith(".excalidraw"):
            svg_filename = os.path.splitext(filename)[0] + ".svg"
            destination_path = os.path.join(destination_folder, svg_filename)
            result = subprocess.run(["excalidraw-to-svg", asset_path, destination_path])
            if result.returncode != 0:
                print(f"Failed to convert {asset_path} to SVG.")
                continue  # Skip to the next file
        else:
            destination_path = os.path.join(destination_folder, filename)
            shutil.copy(asset_path, destination_path)
