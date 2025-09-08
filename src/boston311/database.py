"""Database operations for the Boston 311 dashboard."""

from pathlib import Path

import duckdb
import panel as pn

from boston311.config import config
from boston311.sql_utils import SQLUtils


@pn.cache
def init_duckdb(file_path: Path) -> duckdb.DuckDBPyConnection:
    """Initialize DuckDB connection with spatial extension and load data.

    Args:
        file_path: Path to the parquet files

    Returns:
        DuckDB connection object
    """
    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")

    # Load all data without time filtering - using Path directly is safe here
    con.sql(f"CREATE TABLE requests AS SELECT * FROM '{file_path}'")
    return con


@pn.cache
def get_neighborhoods(
    con: duckdb.DuckDBPyConnection,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[str]:
    """Get list of available neighborhoods with optional time filtering.

    Args:
        con: DuckDB connection
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        List of neighborhood names plus "All" option
    """
    time_filter = SQLUtils.build_time_filter(start_date, end_date)
    query = SQLUtils.build_distinct_column_query("neighborhood", time_filter)

    df = con.sql(query).fetchdf()
    if df is None or df.empty:
        return ["All"]
    return df["neighborhood"].tolist() + ["All"]


@pn.cache
def get_sources(
    con: duckdb.DuckDBPyConnection,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[str]:
    """Get list of available sources with optional time filtering.

    Args:
        con: DuckDB connection
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        List of source names plus "All" option
    """
    time_filter = SQLUtils.build_time_filter(start_date, end_date)
    query = SQLUtils.build_distinct_column_query("source", time_filter)

    df = con.sql(query).fetchdf()
    if df is None or df.empty:
        return ["All"]
    return df["source"].tolist() + ["All"]


@pn.cache
def get_subjects(
    con: duckdb.DuckDBPyConnection,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[str]:
    """Get list of available subjects with optional time filtering.

    Args:
        con: DuckDB connection
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        List of subject names plus "All" option
    """
    time_filter = SQLUtils.build_time_filter(start_date, end_date)
    query = SQLUtils.build_distinct_column_query("subject", time_filter)

    df = con.sql(query).fetchdf()
    if df is None or df.empty:
        return ["All"]
    return df["subject"].tolist() + ["All"]


# Initialize database connection
con = init_duckdb(config.DATA_PATH)
