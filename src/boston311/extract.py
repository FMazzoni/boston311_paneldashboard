"""
This script extracts the service requests data from the Boston 311 dataset.
"""

import logging
import re

import duckdb
import requests

log = logging.getLogger(__name__)
BASE_URL = "https://data.boston.gov"


def get_service_requests_urls() -> list[tuple[str, str]]:
    url = "https://data.boston.gov/dataset/311-service-requests"

    log.info("Fetching Boston 311 dataset page...")
    response = requests.get(url)
    html = response.text

    log.info("Parsing HTML for CSV download links...")
    # Pattern to match both href and aria-label from the download buttons
    pattern = r'<a href="(https://data\.boston\.gov/dataset/[a-f0-9-]+/resource/[a-f0-9-]+/download/tmp[a-z0-9_]+\.csv)"[^>]*aria-label="([^"]*)"'
    matches = re.findall(pattern, html)

    log.info(f"Found {len(matches)} CSV download links")
    for url, label in matches:
        log.info(f"  - {label.strip()}")

    return matches


def save_out_to_parquet(url: str, output_path: str):
    log.info(f"Downloading CSV from: {url}")

    con = duckdb.connect()
    log.info("Installing DuckDB spatial extension...")
    con.install_extension("spatial")
    con.load_extension("spatial")

    log.info("Reading CSV data...")
    service_requests_raw = con.read_csv(url)  # noqa: F841

    log.info("Processing spatial data and converting to Parquet...")
    sql = """
        SELECT 
            *,
            CASE 
                WHEN geom_4326 IS NOT NULL 
                THEN ST_GeomFromHEXEWKB(geom_4326) 
            ELSE NULL 
            END as geometry
        FROM service_requests_raw
        WHERE geom_4326 IS NOT NULL 
        """
    con.sql(f"COPY ({sql}) TO '{output_path}' (FORMAT 'parquet')")
    log.info(f"Saved to: {output_path}")


def main():
    # Configure logging when script is run directly
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    log.info("Starting Boston 311 data extraction...")
    urls_and_titles = get_service_requests_urls()

    log.info(f"Processing {len(urls_and_titles)} files...")
    for i, (url, title) in enumerate(urls_and_titles, 1):
        log.info(f"Processing file {i}/{len(urls_and_titles)}: {title.strip()}")
        clean_title = title.strip().replace(" ", "_").replace("/", "_")
        save_out_to_parquet(url, f"data/raw/{clean_title}.parquet")

    log.info("Data extraction completed!")


if __name__ == "__main__":
    main()
