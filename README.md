# Boston 311 Service Requests Dashboard

An **interactive geospatial dashboard** for exploring Boston's 311 service request data from 2011-2025, built with modern Python data visualization technologies.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Panel](https://img.shields.io/badge/Panel-Dashboard-orange)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-yellow)

## 🎯 Features

- **🗺️ Interactive Geospatial Visualization** - GPU-accelerated mapping with Lonboard
- **📊 Dynamic Filtering** - Time periods, neighborhoods, sources, and service types
- **🎨 Color-coded Analysis** - Visual patterns by category with interactive legends  
- **📋 Data Selection** - Click points or select areas to view detailed records
- **⚡ High Performance** - DuckDB for fast analytics on large datasets
- **📱 Modern UI** - Responsive design with dark theme

## 🏗️ Architecture

The application follows a modular architecture with clear separation of concerns:

```
src/boston311/
├── app.py              # Main application entry point
├── config.py           # Centralized configuration
├── dashboard.py        # Main StateViewer dashboard component
├── database.py         # Database operations and data fetching
├── time_periods.py     # Dynamic time period utilities
├── color_mapping.py    # Color mapping and visualization utilities
├── sql_utils.py        # Safe SQL query construction
├── ui_components.py    # Reusable UI components
├── logging_utils.py    # Logging configuration utilities
└── extract.py          # Data preprocessing script
```

### Key Design Principles

- **🔒 Security First** - SQL injection prevention with parameterized queries
- **⚡ Performance** - Cached operations and GPU acceleration
- **🧪 Testability** - Modular components with clear interfaces
- **📝 Type Safety** - Comprehensive type hints throughout
- **🔄 Fail-Fast** - Standard Python exceptions for clear error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd boston311
   ```

2. **Install dependencies**

   ```bash
   # Using UV (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Extract and prepare data** (see Data Extraction section below)

4. **Run the dashboard**

   ```bash
   # Using UV
   uv run panel serve src/boston311/app.py --show --autoreload
   
   # Or using Python directly
   python -m panel serve src/boston311/app.py --show --autoreload
   ```

## 📊 Data Extraction

The dashboard requires Boston 311 service request data to be preprocessed from the city's open data portal.

### Automated Data Extraction

The `extract.py` script automatically downloads and processes the data:

```bash
# Run the extraction script
uv run python src/boston311/extract.py

# This will:
# 1. Scrape https://data.boston.gov/dataset/311-service-requests
# 2. Download all available CSV files (2011-2025)
# 3. Convert to Parquet format with spatial geometry processing
# 4. Save to data/raw/ directory
```

### Data Processing Steps

1. **🌐 Web Scraping** - Automatically discovers CSV download URLs from the Boston data portal
2. **📥 Download** - Fetches CSV files for each year (2011-2025)
3. **🗺️ Spatial Processing** - Converts WKB geometry to PostGIS-compatible format using DuckDB spatial extension
4. **💾 Parquet Conversion** - Saves as efficient Parquet files for fast analytics
5. **🧹 Data Cleaning** - Filters out records without valid geometry

### Manual Data Setup

If you prefer to download data manually:

1. Visit [Boston 311 Service Requests](https://data.boston.gov/dataset/311-service-requests)
2. Download CSV files for desired years
3. Place files in `data/raw/` directory
4. Run the extraction script to convert to Parquet format

### Data Schema

The processed data includes these key fields:

- **`open_dt`** - Request submission timestamp
- **`source`** - How the request was submitted (App, Phone, etc.)
- **`subject`** - Type of service request
- **`neighborhood`** - Boston neighborhood
- **`geometry`** - Spatial coordinates (Point geometry)

## 🎛️ Configuration

All configuration is centralized in `config.py`:

```python
# UI Settings
MAP_HEIGHT = 600
TABLE_HEIGHT = 400
MAX_DISPLAY_RECORDS = 100

# Performance Limits  
MAX_SELECTION_RECORDS = 1000

# Color Schemes
DEFAULT_POINT_COLOR = (255, 140, 0, 255)
```

## 🔧 Development

### Project Structure

- **`config.py`** - Application configuration and constants
- **`database.py`** - Database operations and data fetching with caching
- **`time_periods.py`** - Dynamic time period generation (relative dates)
- **`color_mapping.py`** - Stable color mapping for categorical data
- **`sql_utils.py`** - Safe SQL query construction (injection prevention)
- **`ui_components.py`** - Reusable UI components (tables, legends)
- **`logging_utils.py`** - Centralized logging configuration
- **`dashboard.py`** - Main StateViewer class with all interaction logic
- **`extract.py`** - Data preprocessing and extraction utilities
- **`app.py`** - Application entry point and Panel template setup

### Code Quality

- **Type Safety** - Full type hints with mypy compatibility
- **Linting** - Ruff for fast Python linting
- **Security** - SQL injection prevention with parameterized queries
- **Performance** - Cached database operations and efficient data structures
- **Modularity** - Clear separation of concerns for maintainability

### Adding New Features

1. **Data Filters** - Add new filter options in `database.py` and update `dashboard.py`
2. **Visualizations** - Extend `color_mapping.py` for new color schemes
3. **UI Components** - Add reusable components in `ui_components.py`
4. **Configuration** - Add new settings to `config.py`

## 📈 Performance

- **⚡ DuckDB** - Columnar analytics engine for fast queries on large datasets
- **🎮 GPU Acceleration** - Lonboard leverages WebGL for smooth map rendering
- **💾 Caching** - Panel caching for database operations and UI components
- **📦 Parquet** - Efficient columnar storage format
- **🔄 Lazy Loading** - Data loaded on-demand based on user selections

## 🙏 Acknowledgments

- **City of Boston** - For providing open access to 311 service request data
- **Panel** - For the excellent dashboard framework
- **DuckDB** - For high-performance analytics capabilities
- **Lonboard** - For GPU-accelerated geospatial visualization

## 🔗 Links

- [Boston Open Data Portal](https://data.boston.gov/)
- [Panel Documentation](https://panel.holoviz.org/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Lonboard Documentation](https://developmentseed.org/lonboard/)
