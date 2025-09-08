"""UI components for the Boston 311 dashboard."""

import panel as pn

from boston311.config import config


def create_table_view(selected_data, show_table: bool):
    """Create a table view for selected data.

    Args:
        selected_data: DuckDB relation containing selected data
        show_table: Whether to show the table

    Returns:
        Panel component for the table view
    """
    # Early returns for edge cases
    if not show_table or selected_data is None:
        return pn.pane.HTML(
            "<div style='text-align: center; color: #6c757d; font-style: italic; padding: 20px;'>Click on a point or select an area to view detailed data</div>",
            margin=10,
        )

    df = selected_data.fetchdf()
    if df.empty:
        return pn.pane.HTML(
            "<div style='text-align: center; color: #6c757d; font-style: italic; padding: 20px;'>No data found in selection</div>",
            margin=10,
        )

    # Get displayable columns (exclude geometry)
    display_columns = [
        col for col in df.columns if col.lower() not in ["geometry", "geom"]
    ]
    if not display_columns:
        return pn.pane.HTML(
            "<div style='text-align: center; color: #6c757d; font-style: italic; padding: 20px;'>No displayable columns found</div>",
            margin=10,
        )

    # Prepare data for display
    df_display = df[display_columns].copy()

    # Format datetime columns
    for col in df_display.columns:
        if df_display[col].dtype == "datetime64[ns]":
            df_display[col] = df_display[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Determine title and limit rows if needed
    total_records = len(df)
    if len(df_display) > config.MAX_DISPLAY_RECORDS:
        df_display = df_display.head(config.MAX_DISPLAY_RECORDS)
        title = f"### Selected Data (showing first {config.MAX_DISPLAY_RECORDS} of {total_records} records)"
    else:
        title = f"### Selected Data ({total_records} records)"

    return pn.Column(
        pn.pane.Markdown(title, margin=(10, 10, 5, 10)),
        pn.pane.DataFrame(
            df_display,
            sizing_mode="stretch_width",
            height=config.TABLE_HEIGHT,
            margin=10,
        ),
        sizing_mode="stretch_width",
    )


def create_color_legend(color_legend, color_column: str):
    """Create a modern color legend widget for the sidebar.

    Args:
        color_legend: Dictionary mapping values to colors
        color_column: Current color column selection

    Returns:
        Panel component for the color legend
    """
    if not color_legend or color_column == "None":
        return pn.pane.HTML(
            "<div style='text-align: center; color: #6c757d; font-style: italic; padding: 20px;'>No color mapping active</div>",
            margin=10,
        )

    # Sort legend items for consistent display - ensure color_legend is a dict
    if not isinstance(color_legend, dict):
        return pn.pane.HTML(
            "<div style='text-align: center; color: #6c757d; font-style: italic; padding: 20px;'>Invalid legend data</div>",
            margin=10,
        )
    sorted_items = sorted(color_legend.items())

    legend_html = """
    <div style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
    """

    for value, color in sorted_items:
        # Handle None values
        display_value = "None" if value == "None" or value is None else str(value)
        # Truncate long values but be more generous with space
        if len(display_value) > 25:
            display_value = display_value[:22] + "..."

        legend_html += f"""
        <div style='display: flex; align-items: center; margin: 4px 0; padding: 6px 8px; 
                   background: rgba(255, 255, 255, 0.08); border-radius: 6px; 
                   box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                   transition: all 0.2s ease; cursor: default; border: 1px solid rgba(255, 255, 255, 0.1);'
             onmouseover='this.style.background="rgba(255, 255, 255, 0.12)"; this.style.transform="translateY(-1px)"; this.style.boxShadow="0 2px 8px rgba(0,0,0,0.3)";'
             onmouseout='this.style.background="rgba(255, 255, 255, 0.08)"; this.style.transform="translateY(0)"; this.style.boxShadow="0 1px 3px rgba(0,0,0,0.2)";'>
            <div style='width: 14px; height: 14px; background-color: {color}; 
                       border: 2px solid rgba(255, 255, 255, 0.3); margin-right: 8px; flex-shrink: 0; 
                       border-radius: 50%; box-shadow: 0 0 0 1px rgba(0,0,0,0.2);'></div>
            <span style='font-size: 12px; font-weight: 500; color: rgba(255, 255, 255, 0.9); line-height: 1.2;'>{display_value}</span>
        </div>
        """
    legend_html += "</div>"

    return pn.pane.HTML(
        legend_html, margin=(0, 10, 10, 10), sizing_mode="stretch_width"
    )
