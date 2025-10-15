#!/usr/bin/env python3
"""Startup script for Hugging Face Spaces deployment."""

import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging to show messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

log = logging.getLogger(__name__)


def ensure_data_exists():
    """Download data from Hugging Face dataset if not present."""
    data_dir = Path("data/raw")

    if data_dir.exists() and list(data_dir.glob("*.parquet")):
        return

    # Download from HF dataset instead of scraping
    import duckdb
    from datasets import load_dataset

    dataset = load_dataset("fmazzoni/boston311-data")

    # log.info("Data not found, running extraction script...")
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "boston311.parquet"

    con = duckdb.connect()
    data = dataset["train"]._data.table
    con.install_extension("spatial")
    con.load_extension("spatial")

    # Load all data without time filtering - using Path directly is safe here
    sql = """
        SELECT 
            * EXCLUDE geometry,
            CASE 
                WHEN geom_4326 IS NOT NULL 
                THEN ST_GeomFromHEXEWKB(geom_4326) 
            ELSE NULL 
            END as geometry
        FROM data
        WHERE geom_4326 IS NOT NULL 
    """
    con.sql(f"COPY ({sql}) TO '{output_path}' (FORMAT 'parquet')")
    log.info(f"Saved to: {output_path}")


def main():
    """Start the Panel application."""
    # Ensure data exists before starting the app
    ensure_data_exists()

    # Set environment variables for Panel/Bokeh
    os.environ["PANEL_ALLOW_WEBSOCKET_ORIGIN"] = "*"
    os.environ["BOKEH_ALLOW_WS_ORIGIN"] = "*"

    # Get the port from environment (Hugging Face uses PORT env var)
    port = os.environ.get("PORT", "7860")

    # Path to the app file
    app_path = Path("src/boston311/app.py")

    if not app_path.exists():
        log.error(f"Error: App file not found at {app_path}")
        sys.exit(1)

    # Command to run Panel (uv environment is already active)
    cmd = [
        "panel",
        "serve",
        str(app_path),
        "--port",
        port,
        "--allow-websocket-origin",
        "*",
        "--show",
    ]

    log.info(f"Starting Panel app on port {port}...")
    log.info(f"Command: {' '.join(cmd)}")

    subprocess.run(cmd)


if __name__ == "__main__":
    main()
