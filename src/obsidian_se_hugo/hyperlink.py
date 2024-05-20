from dataclasses import dataclass


@dataclass
class Hyperlink:
    """Represents a hyperlink with a link and an optional alias."""

    link: str  # Mandatory link URL (string)
    alias: str = None  # Optional alias for the link (string)
    section: str = None  # Optional section for the link after `#`
