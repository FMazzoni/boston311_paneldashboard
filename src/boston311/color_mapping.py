"""Color mapping utilities for the Boston 311 dashboard."""

from typing import Any, Literal

import colorcet as cc
import duckdb
import panel as pn
from lonboard.colormap import apply_categorical_cmap

from boston311.config import config
from boston311.database import con
from boston311.sql_utils import SQLUtils


def to_rgb(hex: str) -> list[int]:
    """Convert hex color to RGB list."""
    h = hex.strip("#")
    return list(int(h[i : i + 2], 16) for i in (0, 2, 4))


@pn.cache
def get_global_color_mappings(
    con: duckdb.DuckDBPyConnection,
) -> dict[str, dict[str, list[int]]]:
    """Create stable color mappings for all columns based on the full dataset.

    Args:
        con: DuckDB connection

    Returns:
        Dictionary mapping column names to color mappings
    """
    color_mappings: dict[str, dict[str, list[int]]] = {}
    colors = [to_rgb(hex_color) for hex_color in cc.palette["glasbey_category10"]]

    for column in config.COLOR_COLUMNS:
        # Get all unique values from the full dataset using safe query building
        query = SQLUtils.build_distinct_column_query(column)
        unique_values = [row[0] for row in con.sql(query).fetchall()]

        # Create stable color mapping - store RGB directly
        color_mappings[column] = {
            value: colors[i % len(colors)] for i, value in enumerate(unique_values)
        }
        # Add mapping for None values
        color_mappings[column]["None"] = list(config.NULL_VALUE_COLOR)

    return color_mappings


def map_column_to_color(
    duckframe: duckdb.DuckDBPyRelation,
    column: Literal["source", "subject", "neighborhood"],
    alpha: float = 1.0,
    return_legend: bool = False,
) -> tuple[Any, dict[str, str]] | Any:
    """Map column values to colors using stable global color mappings.

    Args:
        duckframe: DuckDB relation containing the data
        column: Column name to map colors for (must be a supported column)
        alpha: Alpha transparency value (0.0-1.0)
        return_legend: Whether to return legend data along with colors

    Returns:
        Color array, or tuple of (color_array, legend_data) if return_legend=True

    """
    # Validate column name
    validated_column = SQLUtils.validate_column_name(column)

    # Use the global color mapping for this column (already in RGB format)
    rgb_color_map = GLOBAL_COLOR_MAPPINGS.get(validated_column, {})

    # Early returns for edge cases
    if not rgb_color_map:
        return ([], {}) if return_legend else []

    values_df = con.sql(
        f"SELECT {validated_column}::VARCHAR as value FROM duckframe"
    ).fetchdf()
    if values_df.empty:
        return ([], {}) if return_legend else []

    # Apply the categorical colormap using stable mappings
    color_array = apply_categorical_cmap(
        values_df["value"].astype(str),
        rgb_color_map,
        alpha=int(alpha * 255),
    )

    # Return with legend if requested
    if not return_legend:
        return color_array

    # Generate legend data
    unique_values_in_data = values_df["value"].unique().tolist()
    legend_data = {
        value: f"#{rgb_color_map[value][0]:02x}{rgb_color_map[value][1]:02x}{rgb_color_map[value][2]:02x}"
        for value in unique_values_in_data
        if value in rgb_color_map
    }
    return color_array, legend_data


# Cache the global color mappings
GLOBAL_COLOR_MAPPINGS = get_global_color_mappings(con)
