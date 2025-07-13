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