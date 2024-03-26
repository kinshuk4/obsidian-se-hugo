import os
import shutil
import logging
import re

extension_pattern = r"\.[a-z]+$"  # Matches a dot (.) followed by lowercase letters

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

def has_extension(file_string):
    """Checks if a string has a file extension using regex.

    Args:
        file_string: The string to check for an extension.

    Returns:
        True if the string has an extension, False otherwise.
    """
    return bool(re.search(extension_pattern, file_string))