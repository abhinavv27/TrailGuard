"""Tests for dataset service."""
from app.services.dataset_service import DatasetService


def test_compute_file_hash():
    hash1 = DatasetService._compute_file_hash(b"test data")
    hash2 = DatasetService._compute_file_hash(b"test data")
    hash3 = DatasetService._compute_file_hash(b"different data")
    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64  # SHA256 hex

def test_validate_columns_missing():
    import pandas as pd
    df = pd.DataFrame({"col1": [1, 2]})
    errors = DatasetService.validate_columns(df)
    assert len(errors) > 0
    assert "Missing" in errors[0]

def test_validate_columns_empty():
    import pandas as pd
    df = pd.DataFrame()
    errors = DatasetService.validate_columns(df)
    assert any("empty" in e.lower() for e in errors)
