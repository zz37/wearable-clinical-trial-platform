# Constants, Setup & Config 
import os
import json
import argparse
from wearipedia import get_device
import pandas as pd
import numpy as np

# Transform functions 
from parse_data import (
    transform_hr,
    transform_azm,
    transform_br_stage,
    transform_hrv,
    transform_spo2
)

# Metrics and their transformation functions
METRICS = {
    "hr": transform_hr,
    "hrv": transform_hrv,
    "azm": transform_azm,
    "br": transform_br_stage,
    "spo2": transform_spo2,
}

SUPPORTED_FORMATS = ["json", "csv", "excel"]
EXCEL_MAX_ROWS = 1_048_576

# Directories for export raw and clean data
RAW_DIRECTORY = "data/raw_data"
CLEAN_DIRECTORY = "data/clean_data"
os.makedirs(RAW_DIRECTORY, exist_ok=True)
os.makedirs(CLEAN_DIRECTORY, exist_ok=True)



# Clean up old export files
def clean_exports():
    for directory in [RAW_DIRECTORY, CLEAN_DIRECTORY]:
        try:
            for file in os.listdir(directory):
                if file.endswith((".csv", ".json", ".xlsx")):
                    os.remove(os.path.join(directory, file))
        except FileNotFoundError:
            print(f"INFO: Directory not found: {directory}")


# Main CLI ETL wrapper: 
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--synthetic",action="store_true",help="Use synthetic data (default: False; uses real data if omitted)")
    parser.add_argument("--formats", nargs="+", default=["csv"], choices=SUPPORTED_FORMATS)
    parser.add_argument("--clean", action="store_true", help="Clean export directory before export")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows per file")


if __name__ == "__main__":
    main()