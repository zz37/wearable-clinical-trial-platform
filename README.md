# Wearable Clinical-Trial Challenge

Volunteer challenge submission for the **Stanford Snyder Lab / Wearipedia Team**.  
Goal: design a locally hosted system that extracts, stores, and visualizes **Fitbit Charge 6** data for clinical trials.

## Folder project form and structure

```bash
wearable-clinical-platform/
├── .gitignore            # Git ignore rules
├── main.py               # Entry point to run the platform
├── README.md             # README file for whole prject structure & INFO
├── taskX_README.md       # README file for each task; one per task
│
├── data/                 # Raw and clean simulated Fitbit data
├── notebooks/            # Files of Fitbit .ipynb notebooks
├── db/                   # DB schema, migrations
│
├── etl/                  # Scripts to see, extract, and transform data
├── ingestion/            # Data ingestion pipeline
│
├── api/                  # FastAPI or Flask app for the API
├── dashboard/            # Frontend (React/Dash) Dashboards
│
├── monitoring/           # Health checks, logging
```

## Branch naming

For the Wearable Clinical-Trial Challenge, I will use the following naming pattern for each task as a feature branch.

- One task → one feature branch. 

Pattern: `feature/task-<number>-<name>`

Examples:  
- `feature/task-0a-data-volume-estimation`
- `feature/task-0b-data-extraction`
- `feature/task-1-ingestion-write-flow`
- `feature/task-2-access-read-flow`
- ...


## Current Scope

| Task | Status | Notes |
|------|--------|-------|
| 0.a – Data-volume estimation | ✅ completed | see `task0a_README.md` |
| 0.b – Data extraction        | Working on it |
| 1   – Ingestion / write flow | _pending_      | |
| 2   – Access / read flow     | _pending_      | |
| 3   – Multi-year / multi-user optimizations | _pending_ | |
| 4   – Dashboard              | _pending_ | |
| 5   – Monitoring / alerting  | _pending_ | |
| 6   – Horizontal scaling (opt.) | _pending_ | |


## Why this project exists

* Provide researchers an **on-prem** alternative to cloud-only dashboards.
* Keep the architecture **modular** so additional wearables (Apple Watch, Oura, etc.) can plug in later.
* Emphasize **clean code** and clear documentation—one README per task explaining “what & why”.

## Python Vritual Environment Setup

To run any component (ETL, ingestion, dashboard), set up a Python virtual environment:

```bash
python3 -m venv .venv-fitbit
source .venv-fitbit/bin/activate
pip install -r requirements.txt
```

To update `requirements.txt` after installing new packages:

```bash
pip freeze > requirements.txt
```
