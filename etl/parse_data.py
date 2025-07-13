# etl/parse_data.py
"""
DOCATRING

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

