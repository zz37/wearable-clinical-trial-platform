# tests/test_smoke_export_files.py
"""
Smoke test -> fails if any requested export file is missing.
Usage: 
    pytest -m smoke tests/test_smoke_export_files.py --formats=csv,json,excel
    pytest -m smoke --formats=csv,json,excel	
"""

import pytest
from pathlib import Path

# Export locations
RAW_DIRECTORY = Path(__file__).resolve().parent.parent / "data" / "raw_data"
CLEAN_DIRECTORY = Path(__file__).resolve().parent.parent / "data" / "clean_data"

# Dataset of export metric files
# activity not included
DATASETS = ["br", "azm", "hr", "hrv", "spo2"]

# mark this test as a smoke test
@pytest.mark.smoke
@pytest.mark.parametrize("dataset", DATASETS)
def test_export_files_exist(dataset, expected_extensions):
    # Check raw JSON
    raw_file = RAW_DIRECTORY / f"{dataset}.json"
    assert raw_file.is_file(), f"Missing {raw_file.relative_to(RAW_DIRECTORY.parent)}"

    # Check each clean export
    for ext in expected_extensions:
        clean_file = CLEAN_DIRECTORY / f"{dataset}.{ext}"
        assert clean_file.is_file(), f"Missing {clean_file.relative_to(CLEAN_DIRECTORY.parent)}"