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
