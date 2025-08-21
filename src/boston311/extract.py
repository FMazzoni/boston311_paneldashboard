"""
This script extracts the service requests data from the Boston 311 dataset.
"""

import logging
import re

import duckdb
import requests

BASE_URL = "https://data.boston.gov"


def get_service_requests_urls() -> list[tuple[str, str]]:
    url = "https://data.boston.gov/dataset/311-service-requests"

    response = requests.get(url)
    html = response.text
    # Find all CSV links with their resource IDs and aria-labels

    # Pattern to match both href and aria-label from the download buttons
    pattern = r'<a href="(https://data\.boston\.gov/dataset/[a-f0-9-]+/resource/[a-f0-9-]+/download/tmp[a-z0-9_]+\.csv)"[^>]*aria-label="([^"]*)"'
    matches = re.findall(pattern, html)

    logging.info(f"Found {len(matches)} CSV download links")
    for url, label in matches:
        logging.info(f"{label.strip()}: {url}")

    return matches


def save_out_to_parquet(url: str, output_path: str):
    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")

    service_requests_raw = con.read_csv(url)  # noqa: F841

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


def main():
    urls_and_titles = get_service_requests_urls()
    for url, title in urls_and_titles:
        save_out_to_parquet(url, f"data/raw/{title}.parquet")


if __name__ == "__main__":
    main()
