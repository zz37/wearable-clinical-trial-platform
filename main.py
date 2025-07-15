#!/usr/bin/env python
# main.py
"""
Minimal CLI wrapper to launch ETL 
"""

import subprocess

# For main etl pipeline
def run_etl_pipeline():
    print("\n Run ETL Extraction")
    args = input(
        "Enter ETL args (e.g., --start 2024-12-01 --end 2024-12-10 "
        "--formats csv json excel --synthetic --limit 500):\n> "
    )
    command = ["python", "etl/etl_main.py"] + args.strip().split()
    subprocess.run(command)

# For run smoke tests
def run_smoke_tests():
    print("\n Run Smoke Tests")
    args = input(
        "Enter smoke test args (e.g., --formats=csv,json,excel):\n> "
    )
    command = ["pytest", "-m", "smoke"] + args.strip().split()

    subprocess.run(command)

# ELT sub menu slection
def etl_submenu():
    while True:
        print("\n--- ETL Tools ---")
        print("1. Run ETL pipeline")
        print("2. Run smoke test")
        print("0. Back to main menu")
        choice = input("Select an ETL option: ").strip()

        match choice:
            case "1":
                run_etl_pipeline() # to run the etl ectraction piepline
            case "2":
                run_smoke_tests() # to run only the smoke test for exported formats
            case "0":
                break
            case _:
                print("Invalid option. Try again.")

# For run ingestion to timescaledb databse
def run_ingestion():
    print("\nRun Ingestion to TimescaleDB")
    args = input(
        "Enter ingestion args (e.g., --csv data/clean_data/hr.csv --user 0001):\n> " #  --user 0001 --> to dinsting unique id insertion
    )
    command = ["python", "ingestion/ingest_fitbit.py"] + args.strip().split()
    subprocess.run(command)

# Main Menu
def main_menu():
    while True:
        print("\n=== Wearable Clinical Trial CLI ===")
        print("1. ETL tools")
        print("2. Ingest CSV into TimescaleDB")
        print("0. Exit")
        choice = input("Select an option: ").strip()

        match choice:
            case "1":
                etl_submenu()
            case "2":
                run_ingestion()
            case "0":
                print("Exiting...")
                break
            case _:
                print("Invalid option. Try again.")


if __name__ == "__main__":
    main_menu()
