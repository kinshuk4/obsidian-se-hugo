import os
import shutil
import logging


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