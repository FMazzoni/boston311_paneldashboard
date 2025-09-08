"""Configuration module for the Boston 311 dashboard."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """Centralized configuration for the Boston 311 dashboard."""

    # Data configuration
    DATA_PATH: Path = Path("data/raw/*.parquet")

    # UI configuration
    TABLE_PAGE_SIZE: int = 25
    TABLE_HEIGHT: int = 400
    MAP_HEIGHT: int = 600
    SIDEBAR_WIDTH: int = 350

    # Data limits
    MAX_SELECTION_RECORDS: int = 1000
    MAX_DISPLAY_RECORDS: int = 100

    # Color configuration
    DEFAULT_POINT_COLOR: tuple[int, int, int, int] = (255, 140, 0, 255)
    NULL_VALUE_COLOR: tuple[int, int, int] = (128, 128, 128)

    # Alpha and size bounds
    ALPHA_BOUNDS: tuple[float, float] = (0.0, 1.0)
    SIZE_BOUNDS: tuple[int, int] = (0, 100)

    # Supported columns for color mapping
    COLOR_COLUMNS: tuple[str, ...] = ("source", "subject", "neighborhood")

    # Time period configuration
    MIN_YEAR: int = 2011
    RECENT_YEARS_COUNT: int = 6


# Global configuration instance
config = AppConfig()
