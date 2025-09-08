#!/usr/bin/env python3
"""Startup script for Hugging Face Spaces deployment."""

import os
import subprocess
import sys
from pathlib import Path


def ensure_data_exists():
    """Ensure data exists, download if necessary."""
    data_dir = Path("data/raw")

    # Check if data already exists
    if data_dir.exists() and list(data_dir.glob("*.parquet")):
        print("Data already exists, skipping download.")
        return

    print("Data not found, running extraction script...")
    data_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Run the extraction script using uv
        subprocess.run(["uv", "run", "python", "src/boston311/extract.py"], check=True)
        print("Data extraction completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during data extraction: {e}")
        print("Continuing without data - some features may not work.")


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
        print(f"Error: App file not found at {app_path}")
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
        "--host",
        "0.0.0.0",
        "--show",
    ]

    print(f"Starting Panel app with command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Panel app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
