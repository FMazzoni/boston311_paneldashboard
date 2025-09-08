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
    """Ensure data exists, download if necessary."""
    data_dir = Path("data/raw")

    # Check if data already exists
    if data_dir.exists() and list(data_dir.glob("*.parquet")):
        parquet_files = list(data_dir.glob("*.parquet"))
        log.info(
            f"Data already exists ({len(parquet_files)} files), skipping download."
        )
        return

    log.info("Data not found, running extraction script...")
    data_dir.mkdir(parents=True, exist_ok=True)

    log.info("Starting data extraction process...")
    result = subprocess.run(["uv", "run", "python", "src/boston311/extract.py"])

    if result.returncode == 0:
        log.info("Data extraction completed successfully.")
    else:
        log.error(f"Data extraction failed (exit code {result.returncode})")
        log.warning("Continuing without data - some features may not work.")


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

    # Command to run Panel using uv
    cmd = [
        "uv",
        "run",
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
