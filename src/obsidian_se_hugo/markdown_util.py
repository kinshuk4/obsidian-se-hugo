import logging

import frontmatter
import logging

import logging


def to_be_published(file):
    post = frontmatter.load(file)
    if "published" in post.keys():
        if post["published"] != True:
            return False
        else:
            return True

    logging.debug("File %s has no publish key in frontmatter", str(file))
    return False


def get_markdown_files_to_publish(origin):
    to_publish = []
    for file in origin.rglob("*.md"):
        if to_be_published(file):
            logging.info("TO PUBLISH: %s", str(file))
            to_publish.append(str(file))
    return to_publish
