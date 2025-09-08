"""SQL utilities for safe query construction."""

from boston311.config import config


class SQLUtils:
    """Utilities for safe SQL query construction."""

    @staticmethod
    def validate_column_name(column: str) -> str:
        """Validate column name against whitelist to prevent SQL injection."""
        if column not in config.COLOR_COLUMNS:
            raise ValueError(
                f"Invalid column name: {column}. Must be one of {config.COLOR_COLUMNS}"
            )
        return column

    @staticmethod
    def escape_sql_string(value: str) -> str:
        """Safely escape SQL string values."""
        return value.replace("'", "''")

    @staticmethod
    def build_time_filter(start_date: str | None, end_date: str | None) -> str:
        """Build safe time filter clause."""
        if not start_date or not end_date:
            return ""

        return f" AND open_dt >= '{SQLUtils.escape_sql_string(start_date)}' AND open_dt < '{SQLUtils.escape_sql_string(end_date)}'"

    @staticmethod
    def build_distinct_column_query(column: str, time_filter: str = "") -> str:
        """Build a safe query to get distinct values from a column."""
        validated_column = SQLUtils.validate_column_name(column)
        return f"SELECT DISTINCT {validated_column} FROM requests WHERE {validated_column} IS NOT NULL{time_filter} ORDER BY {validated_column}"
