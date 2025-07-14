# ingestion/ingest_fitbit.py

# libraries
import os
import json
import pandas as pd
import psycopg2
from datetime import datetime

# File Directory
DATA_FILE_DIRECTORY = os.path.join(os.getenv("DATA_DIR", "../data/clean_data/"), "hr.csv")
LAST_OK_RUN_DIRECTORY = "state/last_OK_run.json"


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

