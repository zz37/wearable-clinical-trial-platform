"""
ETL for Fitbit Charge 6 (Wearipedia) → Clean Data → CSV / JSON / Excel.

Raw data in:   data/raw_data/  
Clean data in: data/clean_data/

- Excel (.xlsx) export skips files > 1,048,576 rows. Use --limit to stay under.
- No limit in json and csv.

Example:
  python etl/etl_main.py --start 2024-12-01 --end 2024-12-10 --formats csv json excel --synthetic --limit 500
"""

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

# To fix NumPy types for JSON serialization
def fix_np_types(obj):
    if isinstance(obj, (np.integer,)): return int(obj)
    if isinstance(obj, (np.floating,)): return float(obj)
    return str(obj)

# Clean up old export files
def clean_exports():
    for directory in [RAW_DIRECTORY, CLEAN_DIRECTORY]:
        try:
            for file in os.listdir(directory):
                if file.endswith((".csv", ".json", ".xlsx")):
                    os.remove(os.path.join(directory, file))
        except FileNotFoundError:
            print(f"INFO: Directory not found: {directory}")

# This is for to get raw data and export it to json ONLY
def extract_and_export_raw_data(start_date, end_date, seed=42, synthetic=True, access_token=None):
    device = get_device("fitbit/fitbit_charge_6")

    if synthetic: 
        params = {"seed": seed, "start_date": start_date, "end_date": end_date}
        data = {
        "br": device.get_data("intraday_breath_rate", params),
        "azm": device.get_data("intraday_active_zone_minute", params),
        "hr": device.get_data("intraday_heart_rate", params),
        "hrv": device.get_data("intraday_hrv", params),
        "spo2": device.get_data("intraday_spo2", params),
        # "activity": device.get_data("intraday_activity", params) # Not used
    }
        
    else: # Placeholder, no synth data, -> use acces token
        device.authenticate(access_token)
        # No error recovery here
        raise NotImplementedError("Real data mode not implemented yet.")

    for metric, raw_json in data.items(): # export raw data so i can see it
        path = os.path.join(RAW_DIRECTORY, f"{metric}.json")
        try:
            with open(path, "w") as f:
                json.dump(raw_json, f, indent=2, default=fix_np_types)
            print(f"INFO: [RAW] Saved {metric} to {path}")
        except Exception as exc:
            print(f"ERROR: [RAW] Failed to export {metric}: {exc}")

    return data

# This is for to get trans. clean data
def run_clean_extraction(raw_data, user_params):
    print("INFO: [CLEAN] Transforming and exporting clean data...")

    for metric, transform in METRICS.items():
        # Transform
        try:
            data_frame = transform(raw_data[metric])
        except Exception as exc:
            print(f"WARNING: [CLEAN] Skipped '{metric}': {exc}")
            continue
        if user_params.limit is not None:
            data_frame = data_frame.head(user_params.limit)

        try:
            if "json" in user_params.formats: # export json
                json_path = os.path.join(CLEAN_DIRECTORY, f"{metric}.json")
                data_frame.to_json(json_path, orient="records", indent=2, date_format="iso")
                print(f"INFO: [CLEAN] Saved {metric} (JSON) to {json_path}")

            if "csv" in user_params.formats: # export to csv
                csv_path = os.path.join(CLEAN_DIRECTORY, f"{metric}.csv")
                data_frame.to_csv(csv_path, index=False)
                print(f"INFO: [CLEAN] Saved {metric} (CSV) to {csv_path}")
        
            if "excel" in user_params.formats:
                if len(data_frame) <= EXCEL_MAX_ROWS: # error I found with xlsx export
                    excel_path = os.path.join(CLEAN_DIRECTORY, f"{metric}.xlsx")
                    data_frame.to_excel(excel_path, index=False)
                    print(f"INFO: [CLEAN] Saved {metric} (Excel) to {excel_path}")
                else:
                    print(f"WARNING: Skipped Excel export for {metric}: many rows ({len(data_frame)})")  
        except Exception as exc:
                print(f"ERROR: [CLEAN] Failed to export '{metric}' in formats {user_params.formats}: {exc}")
                print(f"INFO: [CLEAN] Files saved in: {CLEAN_DIRECTORY}/")

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

    args = parser.parse_args()
    
    try:
        if args.clean:
            clean_exports()
            print("INFO: [CLEANUP] Cleaned previous exported files.")
        
        if not args.synthetic:
            raise NotImplementedError("Only synthetic data supported.")

        raw_data = extract_and_export_raw_data(
            start_date=args.start,
            end_date=args.end,
            seed=args.seed,
            synthetic=args.synthetic
            )
        run_clean_extraction(raw_data, args)

    except Exception as exc:
        print(f"ERROR: [ERROR] Process failed: {exc}")
        print(f"ERROR: Raw files path: {RAW_DIRECTORY}/")
        print(f"ERROR: Clean files path: {CLEAN_DIRECTORY}/")

if __name__ == "__main__":
    main()