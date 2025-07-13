# Task 0b – Synthetic Data Extraction (Fitbit Charge 6)

This md docuement provides the documentation of the automated way to extract simulated (synthetic) Fitbit Charge 6 data using the [Wearipedia](https://github.com/Stanford-Health/wearipedia) library, without requiring real device access or credentials.

Note: Synthetic data is generated at 1 Hz (1 data point per second per metric) to simulate the upper-bound volume estimated in Task 0a.

##  What Was Built

The buitl tool is a CLI script located in `etl` with 2 *.py files. Modular approach was used to keep separete transofmrtion logice vs export logic. In the main etl file a approach of try/except block was used for better error tracibility.

1. `parse_data.py` has the transformation functions:
   - Heart Rate (`hr`)
   - Active Zone Minutes (`azm`)
   - Breathing Rate (`br`)
   - Heart Rate Variability (`hrv`)
   - SpO2

Based on the raw data observed in the `fitbit.ipynb` the etl functions use nested `for` loops in order to access each  level and sub-level structure of each metric. Depending of how nested the data was, the use of nested for´s is justified given the incosistency of the data returned by Wearipedia. Special care was given with `.get()` methods for AZM parse, as certain subfields (e.g., `fatBurnActiveZoneMinutes`) were not always present. The transformation step ensures the output is **standardized and consistent**, particularly for CSV export, which in turn will be the intended format for downstream use in `Task 1: Ingestion / Write Flow`. As a future enhancement, parts of the parsing could be refactored using dictionary comprehensions or NumPy arrays for improved performance and readability. As a future enhancement, parts of the parsing could be refactored using dictionary comprehensions or NumPy arrays for improved performance and readability.

CSV files are the selected format for each. metric to simplify downstream ingestion into **TimescaleDB** and analysis in **pandas** or Excel. The raw nested JSON from **Wearipedia** is suitable for archival, but not efficient for time-series ingestion or transformation. All intraday metrics are converted to a unified `timestamp` field (e.g., `2024-01-01 00:01:00`), which supports partitioning and time-based queries in time-series databases.

1. `etl_main.py` uses the transformation functions and CLI flags to get raw and clean data for **Fitbit Waeripedia**. 
   - Time range (`--start`, `--end`)
   - Data reproducibility seed (`--seed`)
   - Output format(s): `csv`, `json`, and/or `excel`
   - Use of synthetic data (`--synthetic`)
   - Clean data (`--data`)
   - Limit the exported data (`--limit`)

As raw jason data was exported a function `fix_np_types()` was created to deal with NumPy types  serilization (e.g., np.float64, np.int64) into native Python float and int. Becaseu Weripedia `data_extract()` was extracting raw json numbers **np(xxxx)** as strings, which could cause problems in later ingestion or numeric processing. With this we make sure data remains ready for downstream use in TimescaleDB or pandas without post-cleaning. When looking to the raw data, overflow precision was observed.This was corrected by rounding to 4 decimal places. 

3. This design favors readability and robustness over unnecessary complexity.

## CLI Example Usage
To generate the data use the below command:

```bash
  python etl/etl_main.py --start 2024-12-01 --end 2024-12-10 --formats csv json excel --synthetic --limit 500
```

> This generates the data in the selected formats and all raw data into `data/raw_data` and clean data to  `data/clean_data` 
> E.g., `data/raw_data/hr.json`, `hr.json`, `hr.xlsx`, etc.


### Why This Design
| Feature              | Why It Helps                                      |
| -------------------- | --------------------------------------------------|
| `--synthetic` flag   | Skip login → go straight to test data             |
| Multiple formats     | CSV → pipelines, JSON → APIs, Excel → quick skim  |
| `notebooks/exports/` | All files land where notebooks can find them      |
| Clear functions      | Easy to test, reuse, or expand                 |
| CLI interface        |  Run with any config → flexible + automatable   |


## Nice to Haves / Future Enhancements
- Add support for real Fitbit data with `access_token`
- Unit tests: Add basic test coverage for extract and transform functionscomplex

## Smoke Test: Verify Exported Files

After running the ETL export, use this test to confirm that *all* expected files were created in `data/raw_data` and `data/clean_data` 

Example of how to run the test, include the formats of the exported files in the ETL.

```bash
pytest -m smoke --formats=csv,json,excel
```
- `confest.py` includes shared configuration and fixtures for smoke tests of export files.
- `test_smoke_exports` is the main logic.
- `pytest.ini` registers the smoke test marker.