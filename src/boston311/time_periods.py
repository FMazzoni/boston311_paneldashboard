"""Time period utilities for the Boston 311 dashboard."""

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from boston311.config import config


def get_time_periods() -> dict[str, tuple[str, str]]:
    """Generate dynamic time period options based on current date.

    Returns:
        Dictionary mapping display names to (start_date, end_date) tuples
    """
    now = datetime.now()
    current_year = now.year
    periods: dict[str, tuple[str, str]] = {}

    # Current and recent years (dynamic based on current date)
    min_year = max(config.MIN_YEAR, current_year - config.RECENT_YEARS_COUNT)
    for year in range(current_year, min_year, -1):
        periods[str(year)] = (
            f"{year}-01-01 00:00:00",
            f"{year + 1}-01-01 00:00:00",
        )

    # Dynamic relative periods
    # Last 30 days
    thirty_days_ago = now - timedelta(days=30)
    periods["Last 30 Days"] = (
        thirty_days_ago.strftime("%Y-%m-%d %H:%M:%S"),
        now.strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Last 90 days
    ninety_days_ago = now - timedelta(days=90)
    periods["Last 90 Days"] = (
        ninety_days_ago.strftime("%Y-%m-%d %H:%M:%S"),
        now.strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Last 6 months
    six_months_ago = now - relativedelta(months=6)
    periods["Last 6 Months"] = (
        six_months_ago.strftime("%Y-%m-%d %H:%M:%S"),
        now.strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Year to date
    year_start = datetime(current_year, 1, 1)
    periods["Year to Date"] = (
        year_start.strftime("%Y-%m-%d %H:%M:%S"),
        now.strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Complete dataset
    periods["Complete Dataset (2011-Present)"] = (
        f"{config.MIN_YEAR}-01-01 00:00:00",
        now.strftime("%Y-%m-%d %H:%M:%S"),
    )

    return periods


# Generate time periods dynamically
TIME_PERIODS = get_time_periods()
