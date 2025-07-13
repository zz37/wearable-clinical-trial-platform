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
