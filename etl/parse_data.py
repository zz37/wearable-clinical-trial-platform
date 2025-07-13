# etl/parse_data.py
"""
Module to transform raw Fitbit Charge 6 intraday data into pd data frames.

Each function parses raw JSON for the given metrics and submetrics (heart_rate,
active_zone_minute, breathing_rate, hrv, spo2) and get a pd data frame.
"""

import pandas as pd
import numpy as np

# Parse  heart rate data raw
def transform_hr(hr_raw_data):
    hr_records = []

    for hr_by_day in hr_raw_data: # lopp by day
        hr_data = hr_by_day["heart_rate_day"][0]
        daily_summary = hr_data["activities-heart"][0]
        hr_entries = hr_data["activities-heart-intraday"]["dataset"]
        date_string= daily_summary["dateTime"]

        for readings in hr_entries: # loop readingd
            hr_records.append({
                "timestamp": f"{date_string} {readings['time']}",
                "heart_rate": round(readings['value'], 4)# np.round works, not always
            })# i found with this to get time and hr data
    return pd.DataFrame(hr_records)

# Parse active zone minutes data raw
def transform_azm(azm_raw_data):
    azm_records = []

    for azm_by_day in azm_raw_data: # azm by minute
        azm_entries = azm_by_day.get("activities-active-zone-minutes-intraday", [])
        
        for day_readings in azm_entries: # looping by day
            date_string = day_readings["dateTime"]
            minute_entries = day_readings["minutes"]

            for minute_data in minute_entries: # loop by minute
                timestamp = f"{date_string} {minute_data['minute']}"
                zone_values = minute_data["value"]

                az_total = zone_values["activeZoneMinutes"]  # azM is always present

                fat = zone_values.get("fatBurnActiveZoneMinutes", 0) #  # One zone per minute, get the one that's present
                cardio = zone_values.get("cardioActiveZoneMinutes", 0)
                peak = zone_values.get("peakActiveZoneMinutes", 0)

                # Optionally validate only one is active
                if sum([fat, cardio, peak]) > 1:
                    raise ValueError(f"Multiple zones active at {timestamp}")

                azm_records.append({
                    "timestamp": timestamp,
                    "activeZoneMinutes": az_total,
                    "fat_burn": fat,
                    "cardio": cardio,
                    "peak": peak,
                    "zone_type": (
                        "fat_burn" if fat else
                        "cardio" if cardio else
                        "peak" if peak else
                        "none"
                    )
                })

    return pd.DataFrame(azm_records)

# Parse breathing rate data by sleep stage data raw
def transform_br_stage(br_stage_raw_data):
    br_records = []

    for br_by_day in br_stage_raw_data: # loop days
        for br_entry in br_by_day["br"]: # loop by br chunks
            date_string = br_entry["dateTime"],
            stage_data = br_entry["value"]

            for stage_name, stage_metrics in stage_data.items(): # loop sleep stages
                br_records.append({
                    "date": date_string,
                    "sleep_stage": stage_name,
                    "breathing_rate": np.round(stage_metrics["breathingRate"], 4),
                })
    return pd.DataFrame(br_records)

# Parse HRV data raw
def transform_hrv(hrv_raw_data):
    hrv_records = [] 

    for hrv_by_day in hrv_raw_data: # loop by day
        hrv_data = hrv_by_day["hrv"][0]  # summary block
        minute_entries = hrv_data["minutes"]

        for minute_entry in minute_entries: 
            hrv_metrics = minute_entry["value"] # vals
            hrv_records.append({
                "timestamp": minute_entry["minute"],
                "rmssd": round(hrv_metrics["rmssd"], 4),
                "coverage": round(hrv_metrics["coverage"], 4),
                "hf": round(hrv_metrics["hf"], 4),
                "lf": round(hrv_metrics["lf"], 4),
            })

    return pd.DataFrame(hrv_records)

# Parse SpO2 data raw
def transform_spo2(spo2_raw_data):
    spo2_records = [] # store minute-level data

    for spo2_by_day in spo2_raw_data: # loop by day
        for minute_entry in spo2_by_day["minutes"]:  # loop by minute
            spo2_records.append({
                "timestamp": minute_entry["minute"],
                "spo2": round(minute_entry["value"], 4)
            })

    return pd.DataFrame(spo2_records)