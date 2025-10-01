"""MyProfit platform portfolio reader."""

from pathlib import Path

import pandas as pd

from .base import BasePortfolioReader


class MyProfitReader(BasePortfolioReader):
    """Reader for MyProfit portfolio files."""

    @staticmethod
    def _parse_brazilian_currency(value: str) -> float:
        """Convert Brazilian currency string to float (e.g., 'R$ 1.234,56' -> 1234.56)."""
        if pd.isna(value) or value == "" or value == "-":
            return 0.0
        # Remove 'R$', spaces, dots (thousands separator) and convert comma to dot
        cleaned = (
            str(value)
            .replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
            .replace(" ", "")
            .strip()
        )
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def read(self) -> pd.DataFrame:
        """
        Read and parse MyProfit portfolio file.

        Returns:
            Standardized portfolio DataFrame
        """
        # MyProfit .xls is actually HTML
        # Detect format and read accordingly
        with open(self.file_path, "rb") as f:
            first_bytes = f.read(10)

        if first_bytes.startswith(b"<html") or first_bytes.startswith(b"<!DOC"):
            # Read as HTML
            df = pd.read_html(self.file_path)[0]
        else:
            # Read as Excel
            df = pd.read_excel(self.file_path, engine="xlrd")

        # Remove rows with all nulls
        df = df.dropna(how="all")

        # Map MyProfit columns to standardized format
        portfolio_df = pd.DataFrame(
            {
                "ticker": df["Ativo"].str.strip(),
                "quantity": pd.to_numeric(df["Qtd"], errors="coerce").abs(),  # Use abs for negative positions
                "avg_price": df["Preço médio"].apply(self._parse_brazilian_currency),
                "current_price": df["Preço atual"].apply(
                    self._parse_brazilian_currency
                ),
                "total_value": df["Total atual"].apply(
                    self._parse_brazilian_currency
                ),
                "source": "MyProfit",
            }
        )

        # Remove rows where ticker is null
        portfolio_df = portfolio_df.dropna(subset=["ticker"])

        # Remove rows with zero or negative total value
        portfolio_df = portfolio_df[portfolio_df["total_value"] > 0]

        return self.validate_data(portfolio_df)
