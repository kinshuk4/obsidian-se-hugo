from dataclasses import dataclass


@dataclass
class ObsidianConfig:
    root_path: str


@dataclass
class HugoConfig:
    root_path: str
    posts_dir: str
    posts_dir_list: set[str]
    images_dir: str
    allowed_frontmatter_keys: set[str]

    def __post_init__(self):
        # Convert list to set if it's not already a set
        if isinstance(self.allowed_frontmatter_keys, list):
            self.allowed_frontmatter_keys = set(self.allowed_frontmatter_keys)
        if isinstance(self.posts_dir_list, list):
            self.posts_dir_list = set(self.posts_dir_list)

@dataclass
class Config:
    """Configuration object for the application."""

    obsidian: ObsidianConfig
    hugo: HugoConfig


def load_config(config_file_path: str) -> Config:
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
    return Config(obsidian=obsidian_config, hugo=hugo_config)
