"""Boston 311 Service Requests Dashboard - Main Application Entry Point.

This module serves as the main entry point for the Boston 311 dashboard application.
The application has been modularized into separate components for better maintainability:

- config: Application configuration and constants
- database: Database operations and data fetching
- time_periods: Dynamic time period utilities
- color_mapping: Color mapping and visualization utilities
- sql_utils: Safe SQL query construction utilities
- ui_components: Reusable UI components
- dashboard: Main StateViewer dashboard component

This modular architecture provides:
- Clear separation of concerns
- Better testability
- Improved maintainability
- Easier code reuse
"""

from datetime import datetime

import panel as pn

from boston311.config import config
from boston311.dashboard import StateViewer

# Create the main dashboard instance
viewer = StateViewer()

# Generate dynamic title based on data availability
current_year = datetime.now().year
template = pn.template.FastListTemplate(
    title=f"🏛️ Boston 311 Service Requests Explorer (2011 - {current_year})",
    sidebar=[viewer.description, viewer.settings_tabs],
    main=[viewer.view],
    main_layout=None,
    theme="dark",
    sidebar_width=config.SIDEBAR_WIDTH,
)

template.servable()
