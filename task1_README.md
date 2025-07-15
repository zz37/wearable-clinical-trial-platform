# Task 1 - Firbit data ingestion flow

This md document provides the documentation of *delta ingestion pipeline* for Fitbit hear rate data. As a high level view, the ingestion is scheduled to run daily via cron job inside a Dockerize Python environment. With the following properties: 

- Loads **intraday heart rate data** from a local CSV (synth Fitbit API data).
- Uses **TimescaleDB** (according to task 0a design) as the database backend.
- Use of **Docker Compose** to have a:
  - A containerized **TimescaleDB** instance
  . A **Python + cron** ingestion env
- Ensures ingestion is **contained** and **incremental** via a last-run state.

## Desgin Overview

As of now, heart rate data is sampled at **1Hz** (1 row per second), this generates big loads of data.

Adding the full dataset daily is huge and not viable. This is why the use of **delta-ingestion** so the last json file creates a basic local state that will record the last timestamp the ingestion script successfully ran.  Like a short-term memory, to know where it left off, so it can only ingest new rows each time.

In concise form it's a daily cron run with the following:

1. Loads `hr.csv`
2. Reads the last run time from the state file
3. Filters new rows where `timestamp > last_OK_run`
4. Inserts only new rows into the TimescaleDB hypertable
5. Updates the state file to record the latest timestamp ingested

I use **TimescaleDB** because it is built to handle time-series data. Also, i am familiar with **PostgreSQL** so it was a littlbe bit more easy to use an extension like TimeScaleDB since its and extension of Postgres. Also, the DB performs fast, and lets high-volume insertions, and time range filterin for quering (Hypertable)

Other time-series options like InfluxDB or Prometheus are viable but, I am not ery familiar with those.

## Schema 

The current schema is defined in `init/init.sql`, with the design attributes of:
- `TIMESTAMPTZ`: for proper handling of timezone-aware timestamps
- `DOUBLE PRECISION`: accurate storage of fractional BPM values
- `PRIMARY KEY`: prevents duplicates and enables upserts
- **Hypertable**: a TimescaleDB table that partitions time-series data


## Containerized Setup

The file if **Docker Compose** launches:

- The `fitbit-db` container running TimescaleDB
- The `fitbit-ingestion` container built from a `Dockerfile` that installs:
    - Python
    - The `fitbit_ingestion.py` script 
    - Adds cron support
    - Runs ingestion once daily via `crontab.txt`

Volumes are mounted to persist:

-  CSV input: `./data/clean_data/`
- Cron logs
- State file: `state/last_OK_run.json`

## Ingestion Strcuture

The Python script `ingest_fitbit.py`, has the functions and constants that connects to the db using Docker credentials environment variables. Then reads and filters rows from the CSV based on the last ingestion time and updates the rows based on the sate of the las run json file, also resolves confilct if the same data is already in the db.

The script was built arouns a main(), with similar approach like the etl.

## How to Test or Use

1. Start the services:`docker compose up --build -d`
2. Check TimescaleDB id present: `docker exec -it fitbit-db psql -U postgres -d fitbit`
3. Once inside the run: 

```sql
\dt                      -- List tables
\d heart_rate            -- View schema
SELECT * FROM heart_rate LIMIT 5;
```
To see if values are in the hyertable 

4. To manually run ingestion use: `docker exec -it fitbit-ingestion python ingest_fitbit.py`
5. If needed, delete the state json file, to reset the state:`rm ingestion/state/last_OK_run.json`

# Files Structure

The files worked in this task are:

- `hr.csv`              
- `init.sql`                     
- `docker-compose.yml`
- `ingest_fitbit.py`
- `Dockerfile`                      
- `crontab.txt`                     
- `state/last_OK_run.json`          
- `task1_README.md`                 

# Linear Diagram
Below is a simple image of the Roadmap for task 1:
```plaintext
                ┌───────────────────────────────────────┐
                │        Docker Compose Setup           │
                ├───────────────────────────────────────┤
                │ - Creates 2 containers:               │
                │     1. TimescaleDB                    │
                │     2. Ingestion (Python + cron)      │
                │ - Mounts volumes for data persistence │
                └───────────────────────────────────────┘
                                   │
                                   v
                       ┌────────────────────┐
                       │     Cron txt       │
                       ├────────────────────┤
                       │ - Runs daily job   │
                       │ - Triggers ingest  │
                       └────────────────────┘
                                   │
                                   v
            ┌─────────────────────────────────────────────┐
            │                 ingest_fitbit.py            │
            ├─────────────────────────────────────────────┤
            │ 1. View `state/last_OK_run.json`            │
            │     → If no there, makes first run          │
            │                                             │
            │ 2. Loads full CSV file.                     │
            │                                             │
            │ 3. Filters rows: timestamp > last_OK_run    |
            │    -> Delta load to avoid duplicate         │               
            │                                             │             
            │ 4. Inserts only new rows into TimescaleDB   │              
            │    -> ON CONFLICT DO NOTHING                │               
            │                                             │               
            │ 5. Updates state with latest run            │              
            └─────────────────────────────────────────────┘              
```