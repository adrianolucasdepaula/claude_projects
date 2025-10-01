"""Tests for portfolio readers."""

import pytest
from pathlib import Path
import pandas as pd
from src.invest.readers.base import BasePortfolioReader


class MockReader(BasePortfolioReader):
    """Mock reader for testing."""

    def read(self) -> pd.DataFrame:
        """Mock read method."""
        return pd.DataFrame(
            {
                "ticker": ["PETR4", "VALE3"],
                "quantity": [100, 200],
                "avg_price": [30.0, 70.0],
                "current_price": [32.0, 68.0],
                "total_value": [3200.0, 13600.0],
                "source": ["Mock", "Mock"],
            }
        )


def test_base_reader_file_not_found():
    """Test that BasePortfolioReader raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        MockReader("non_existent_file.xlsx")


def test_validate_data_success():
    """Test data validation with valid data."""
    # Create a temporary file for testing
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        reader = MockReader(tmp_path)
        df = reader.read()
        validated = reader.validate_data(df)
        assert not validated.empty
        assert "ticker" in validated.columns
    finally:
        tmp_path.unlink()


def test_validate_data_missing_columns():
    """Test data validation with missing columns."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        reader = MockReader(tmp_path)
        invalid_df = pd.DataFrame({"ticker": ["PETR4"]})

        with pytest.raises(ValueError, match="Missing required columns"):
            reader.validate_data(invalid_df)
    finally:
        tmp_path.unlink()
