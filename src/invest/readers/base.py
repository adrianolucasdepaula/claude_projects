"""Base reader class for portfolio data sources."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class BasePortfolioReader(ABC):
    """Abstract base class for portfolio readers."""

    def __init__(self, file_path: str | Path) -> None:
        """
        Initialize the portfolio reader.

        Args:
            file_path: Path to the portfolio file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """
        Read and parse the portfolio file.

        Returns:
            DataFrame with standardized portfolio columns:
            - ticker: Asset ticker/symbol
            - quantity: Number of shares/units
            - avg_price: Average purchase price
            - current_price: Current market price
            - total_value: Total position value
            - source: Data source name
        """
        pass

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate the parsed data.

        Args:
            df: DataFrame to validate

        Returns:
            Validated DataFrame with only required + common optional columns

        Raises:
            ValueError: If data validation fails
        """
        required_columns = [
            "ticker",
            "quantity",
            "avg_price",
            "current_price",
            "total_value",
            "source",
        ]
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Keep only required columns and common optional ones
        common_optional = ["institution", "asset_type", "asset_class", "category"]
        columns_to_keep = required_columns + [
            col for col in common_optional if col in df.columns
        ]

        return df[columns_to_keep].copy()
