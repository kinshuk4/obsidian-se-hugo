from dataclasses import dataclass
import logging

@dataclass
class ObsidianConfig:
    root_path: str


@dataclass
class HugoConfig:
    root_path: str
    posts_dir: str
    posts_dir_list: list[str]
    images_dir: str
    allowed_frontmatter_keys: set[str]
    manual_content_dir: str
    content_dir: str
    content_images_dir: str

    def __post_init__(self):
        # Convert list to set if it's not already a set
        if isinstance(self.allowed_frontmatter_keys, list):
            self.allowed_frontmatter_keys = set(self.allowed_frontmatter_keys)


@dataclass
class Config:
    """Configuration object for the application."""

    obsidian: ObsidianConfig
    hugo: HugoConfig


def load_config(config_file_path: str, logger: logging.Logger = logging.getLogger(__name__)) -> Config:
    """Loads configuration from a YAML file.

    Args:
        config_file_path (str): Path to the YAML configuration file.

    Returns:
        Config: A Config object containing the loaded configuration.
    """

    import yaml

    with open(config_file_path, "r") as config_file:
        config_data = yaml.safe_load(config_file)
    obsidian_config = ObsidianConfig(**config_data["obsidian"])
    hugo_config = HugoConfig(**config_data["hugo"])
    logger.debug(f"Loaded configuration successfully: {config_data}")
    return Config(obsidian=obsidian_config, hugo=hugo_config)
