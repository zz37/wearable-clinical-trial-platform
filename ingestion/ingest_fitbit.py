# ingestion/ingest_fitbit.py

import os
import json
import pandas as pd
import psycopg2
from datetime import datetime

# Paths
DATA_FILE = os.path.join(os.getenv("DATA_DIR", "../data/clean_data/"), "hr.csv")
LAST_RUN_PATH = "state/last_OK_run.json"


# ---------- DB Connect ----------

def connect():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", 5432),
        dbname=os.getenv("PGDATABASE", "fitbit"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
    )

# ---------- Load last run ----------

def get_last_run_time():
    try:
        with open(LAST_RUN_PATH, "r") as f:
            return datetime.fromisoformat(json.load(f)["last_run"])
    except Exception:
        return None

def save_last_run_time():
    with open(LAST_RUN_PATH, "w") as f:
        json.dump({"last_run": datetime.utcnow().isoformat()}, f)

# ---------- Ingest CSV ----------

def ingest():
    last_run = get_last_run_time()
    print(f"🕒 Last run: {last_run}")

    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])

    if last_run:
        df = df[df["timestamp"] > last_run]

    if df.empty:
        print("✅ No new data to ingest.")
        return

    with connect() as conn, conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(
                "INSERT INTO heart_rate (timestamp, value) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (row["timestamp"], row["value"]),
            )
        conn.commit()

    print(f"✅ Ingested {len(df)} new rows.")
    save_last_run_time()

if __name__ == "__main__":
    ingest()
