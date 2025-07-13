# ===== Constants, Setup & Config =====
import os
import json
import argparse
from wearipedia import get_device
import pandas as pd
import numpy as np





SUPPORTED_FORMATS = ["json", "csv", "excel"]
EXCEL_MAX_ROWS = 1_048_576

# Directories for export raw and clean data
RAW_DIRECTORY = "data/raw_data"
CLEAN_DIRECTORY = "data/clean_data"
os.makedirs(RAW_DIRECTORY, exist_ok=True)
os.makedirs(CLEAN_DIRECTORY, exist_ok=True)

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