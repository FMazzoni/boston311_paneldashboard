"""Main dashboard component for the Boston 311 application."""

from typing import Literal, cast

import duckdb
import panel as pn
import param
from lonboard._layer import ScatterplotLayer
from lonboard._map import Map
from lonboard._viewport import compute_view

from boston311.color_mapping import map_column_to_color
from boston311.config import config
from boston311.database import con, get_neighborhoods, get_sources, get_subjects
from boston311.logging_utils import get_logger
from boston311.sql_utils import SQLUtils
from boston311.time_periods import TIME_PERIODS
from boston311.ui_components import create_color_legend, create_table_view

log = get_logger(name="dashboard")

pn.extension("ipywidgets")

# Dashboard description
description = """# Boston 311 Service Requests Explorer

An **interactive geospatial dashboard** for exploring Boston's 311 service request data from 2011-2025.

🏙️ **Explore** service patterns across neighborhoods  
📊 **Analyze** request types, sources, and temporal trends  
🗺️ **Visualize** geographic distributions with dynamic filtering  

Built with modern web technologies including **Lonboard** for GPU-accelerated mapping, **DuckDB** for high-performance analytics, and **Panel** for interactive dashboards."""


class StateViewer(pn.viewable.Viewer):
    """Main dashboard component for Boston 311 service requests visualization.

    This class provides an interactive geospatial dashboard with:
    - Dynamic time period filtering
    - Geographic filtering by neighborhood
    - Service type and source filtering
    - Interactive map visualization with point selection
    - Tabular data view for selected records
    - Color-coded visualization options

    The component follows modern UI patterns with proper error handling,
    input validation, and configuration management suitable for enterprise use.
    """

    lb_map = cast(
        Map, param.ClassSelector(class_=Map, doc="The map object", constant=True)
    )
    time_period = cast(
        str,
        param.Selector(
            default="Year to Date",
            objects=list(TIME_PERIODS.keys()),
            doc="Time period to display data for",
        ),
    )
    neighborhood = param.Selector(
        default="All", objects=get_neighborhoods(con, *TIME_PERIODS["Year to Date"])
    )
    source = param.Selector(
        default="All", objects=get_sources(con, *TIME_PERIODS["Year to Date"])
    )
    subject = param.Selector(
        default="All", objects=get_subjects(con, *TIME_PERIODS["Year to Date"])
    )
    color_column = cast(
        str,
        param.Selector(
            default="None",
            objects=["None"] + list(config.COLOR_COLUMNS),
        ),
    )
    alpha = cast(float, param.Number(default=0.8, bounds=config.ALPHA_BOUNDS))
    size = cast(int, param.Number(default=5, bounds=config.SIZE_BOUNDS))
    query = cast(str, param.String(default="SELECT * FROM requests"))
    data = param.Parameter(
        default=None,
        doc="The DuckDB relation object",
        constant=False,
    )
    color_legend = cast(
        dict[str, str],
        param.Dict(
            default={},
            doc="Color legend mapping values to hex colors",
            constant=False,
        ),
    )
    selected_data = param.Parameter(
        default=None,
        allow_None=True,
        doc="Selected data for table view",
        constant=False,
    )
    show_table = cast(
        bool,
        param.Boolean(
            default=False,
            doc="Whether to show the table view",
            constant=False,
        ),
    )

    def __init__(self, **params):
        params["lb_map"] = params.get(
            "lb_map",
            Map(
                layers=[],
                view_state={
                    "longitude": -71.0589,
                    "latitude": 42.3601,
                    "zoom": 10,
                },
                show_side_panel=False,
                _height=config.MAP_HEIGHT,
            ),
        )

        super().__init__(**params)

        # Set up bounding box selection observer
        self.lb_map.observe(
            self._handle_bbox_selection_change, names=["selected_bounds"]
        )

        self.description = pn.pane.Markdown(description, margin=5)

        # Filter settings tab
        self.filter_settings = pn.Column(
            pn.pane.Markdown("### Data Filters"),
            pn.widgets.Select.from_param(self.param.time_period),
            pn.widgets.Select.from_param(self.param.neighborhood),
            pn.widgets.Select.from_param(self.param.source),
            pn.widgets.Select.from_param(self.param.subject),
        )

        # Style settings tab
        self.style_settings = pn.Column(
            pn.pane.Markdown("### Visual Styling"),
            pn.widgets.Select.from_param(self.param.color_column),
            pn.widgets.FloatSlider.from_param(self.param.alpha),
            pn.widgets.FloatSlider.from_param(self.param.size),
            margin=5,
        )

        # Create tabs for settings
        self.settings_tabs = pn.Tabs(
            ("🔍 Filters", self.filter_settings),
            ("🎨 Style", self.style_settings),
            dynamic=True,
            tabs_location="above",
            margin=5,
        )

        self.view = pn.Column(
            self._title,
            pn.Row(
                pn.pane.IPyWidget(
                    self.lb_map,
                    sizing_mode="stretch_both",
                ),
                pn.Column(
                    pn.pane.Markdown("### Legend", margin=(10, 10, 5, 10)),
                    self._color_legend,
                    width=250,
                    height=600,  # Fixed height to prevent overflow
                    margin=5,
                    styles={
                        "background": "rgba(255, 255, 255, 0.1)",  # Semi-transparent for dark mode
                        "border-radius": "8px",
                        "border": "1px solid rgba(255, 255, 255, 0.2)",
                        "backdrop-filter": "blur(10px)",
                    },
                    scroll=True,  # Enable scrolling for overflow
                ),
                sizing_mode="stretch_both",
            ),
            self._table_view,  # Add table view below the map
            sizing_mode="stretch_width",
        )

    def _build_filter_conditions(self) -> list[str]:
        """Build common filter conditions based on current selections."""
        conditions = ["geometry IS NOT NULL"]

        # Add time period filtering
        start_date, end_date = TIME_PERIODS[self.time_period]
        conditions.append(f"open_dt >= '{start_date}' AND open_dt < '{end_date}'")

        # Add neighborhood filter
        if self.neighborhood != "All" and isinstance(self.neighborhood, str):
            escaped_neighborhood = SQLUtils.escape_sql_string(self.neighborhood)
            conditions.append(f"neighborhood = '{escaped_neighborhood}'")

        # Add source filter
        if self.source != "All" and isinstance(self.source, str):
            escaped_source = SQLUtils.escape_sql_string(self.source)
            conditions.append(f"source = '{escaped_source}'")

        # Add subject filter
        if self.subject != "All" and isinstance(self.subject, str):
            escaped_subject = SQLUtils.escape_sql_string(self.subject)
            conditions.append(f"subject = '{escaped_subject}'")

        return conditions

    @param.depends("time_period", watch=True, on_init=True)
    def _update_time_period(self):
        """Update the selector options for the selected time period."""
        start_date, end_date = TIME_PERIODS[self.time_period]

        # Update the selector options since the available values might have changed
        self.param.neighborhood.objects = get_neighborhoods(con, start_date, end_date)
        self.param.source.objects = get_sources(con, start_date, end_date)
        self.param.subject.objects = get_subjects(con, start_date, end_date)

        # Reset filters to "All" when time period changes to avoid invalid selections
        self.neighborhood = "All"
        self.source = "All"
        self.subject = "All"

    @param.depends(
        "time_period", "neighborhood", "source", "subject", watch=True, on_init=True
    )
    def _update_data(self):
        """Build dynamic SQL query based on current filters - cached by parameters"""
        where_conditions = self._build_filter_conditions()
        where_clause = " AND ".join(where_conditions)

        query = f"""
            SELECT 
            source,
            subject,
            neighborhood,
            open_dt,
            geometry,
            FROM requests 
            WHERE {where_clause}
            ORDER BY open_dt DESC
        """
        log.info(f"Query: {query}")
        self.data = con.sql(query)

    @param.depends("data", "color_column", "alpha", "size", watch=True)
    def _update_value(self):
        # Type guard to ensure data is available and is a DuckDB relation
        if self.data is None or not isinstance(self.data, duckdb.DuckDBPyRelation):
            return

        if self.color_column == "None":
            get_fill_color = [*config.DEFAULT_POINT_COLOR[:3], int(self.alpha * 255)]
            self.color_legend = {}  # Clear legend when no color column
        else:
            get_fill_color, legend_data = map_column_to_color(
                self.data,
                cast(Literal["source", "subject", "neighborhood"], self.color_column),
                self.alpha,
                return_legend=True,
            )
            self.color_legend = legend_data

        layer = ScatterplotLayer.from_duckdb(
            self.data,
            get_fill_color=get_fill_color,
            pickable=True,
            get_radius=self.size,
            auto_highlight=True,
            crs="EPSG:4326",
        )

        # Set up selection observer for point clicks
        layer.observe(self._handle_point_selection, names=["selected_index"])

        self.lb_map.layers = [layer]

    def _handle_point_selection(self, change):
        """Handle point selection from the layer."""
        selected_index = change.get("new")
        log.info(f"Point selected at index: {selected_index}")

        if selected_index is None:
            self.show_table = False
            self.selected_data = None
            return

        # Build query to get the specific selected row
        where_conditions = self._build_filter_conditions()
        where_clause = " AND ".join(where_conditions)

        # Create a query to get the specific selected row
        query = f"""
            WITH numbered_data AS (
                SELECT *, ROW_NUMBER() OVER (ORDER BY open_dt DESC) - 1 as row_index
                FROM (
                    SELECT 
                        source,
                        subject,
                        neighborhood,
                        open_dt,
                        geometry
                    FROM requests 
                    WHERE {where_clause}
                    ORDER BY open_dt DESC
                )
            )
            SELECT * FROM numbered_data WHERE row_index = {selected_index}
        """

        self.selected_data = con.sql(query)
        self.show_table = True
        log.info(f"Point selection successful for index: {selected_index}")

    def _handle_bbox_selection_change(self, change):
        """Handle bounding box selection change from the map."""
        bounds = change.get("new")
        self._handle_bbox_selection(bounds)

    def _handle_bbox_selection(self, bounds):
        """Handle bounding box selection."""
        # Early return for invalid bounds
        if not bounds or len(bounds) != 4:
            self.show_table = False
            self.selected_data = None
            return

        minx, miny, maxx, maxy = bounds
        log.info(f"Bounding box selected: {bounds}")

        # Build base filter conditions and add spatial filter
        where_conditions = self._build_filter_conditions()
        where_conditions.append(f"""
            ST_X(geometry) BETWEEN {minx} AND {maxx} 
            AND ST_Y(geometry) BETWEEN {miny} AND {maxy}
        """)

        where_clause = " AND ".join(where_conditions)
        query = f"""
            SELECT 
                source,
                subject,
                neighborhood,
                open_dt,
                geometry
            FROM requests 
            WHERE {where_clause}
            ORDER BY open_dt DESC
            LIMIT {config.MAX_SELECTION_RECORDS}
        """

        self.selected_data = con.sql(query)
        self.show_table = True
        log.info("Bounding box selection successful")

    @param.depends("data", watch=True)
    def _fly_to_center(self):
        # Type guard to ensure data is available and layers exist
        if not self.lb_map.layers:
            return

        computed_view_state = compute_view(self.lb_map.layers)
        log.info(f"Computed view state: {computed_view_state}")
        self.lb_map.set_view_state(**computed_view_state)

    @param.depends("selected_data", "show_table")
    def _table_view(self):
        """Create a table view for selected data."""
        return create_table_view(self.selected_data, self.show_table)

    @param.depends("color_legend")
    def _color_legend(self):
        """Create a modern color legend widget for the sidebar."""
        return create_color_legend(self.color_legend, self.color_column)

    def _title(self):
        """Generate a simple, friendly title."""
        return "# Boston 311 Dashboard"
