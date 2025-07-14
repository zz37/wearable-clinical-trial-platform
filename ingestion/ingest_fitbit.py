# ingestion/ingest_fitbit.py

# libraries
import os
import json
import pandas as pd
import psycopg2
from datetime import datetime, timezone

# File Directory
CLEAN_DATA_FILE_DIRECTORY = os.path.join(os.getenv("DATA_DIR", "../data/clean_data/"), "hr.csv")
LAST_OK_RUN_DIRECTORY = "state/last_OK_run.json"


DB_CONFIGURATION = { # based on docker compose file admyn values
    "host": os.getenv("PGHOST", "localhost"), 
    "port": int(os.getenv("PGPORT", 5432)),
    "dbname": os.getenv("PGDATABASE", "fitbit"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
}

# Connect to db
def get_db_connection():
    return psycopg2.connect(**DB_CONFIGURATION)

# LOad last OK run
def load_last_run():
    if not os.path.exists(LAST_OK_RUN_DIRECTORY): # is last run ok?
        return None
    try:
        with open(LAST_OK_RUN_DIRECTORY, "r") as f:
            return datetime.fromisoformat(json.load(f)["last_OK_run"])
    except Exception:
        return None

# SAve last run based on last time on the json 
def save_last_run():
    os.makedirs(os.path.dirname(LAST_OK_RUN_DIRECTORY), exist_ok=True)
    with open(LAST_OK_RUN_DIRECTORY, "w") as json_entry:
        json.dump({"last_run": datetime.now(timezone.utc).isoformat()}, json_entry)



# REad new data from last ok run
def read_new_data(last_run):
    data_frame = pd.read_csv(CLEAN_DATA_FILE_DIRECTORY, parse_dates=["timestamp"])
    if last_run:
        data_frame = data_frame[data_frame["timestamp"] > last_run]
    return data_frame

# Main ingestion 
def main():

    last_OK_run = load_last_run() # function to load the last ok run based on the timestamp the json has
    print(f"Last run was on : {last_OK_run}")
         
    data_frame = read_new_data(last_OK_run)   # read new data and save it in a dataFrame    

    if data_frame.empty:
        print("No new data to be ingested ")
        return
    
    insert_data(data_frame) # new data is ready, then insert it to the tables
    print(f"Ingested {len(data_frame)} new rows.")

    save_last_run() # new data is OK -> log last ingestion in the json for registry

if __name__ == "__main__":
    main()

