"""Kinvo platform portfolio reader."""

import pandas as pd

from .base import BasePortfolioReader


class KinvoReader(BasePortfolioReader):
    """Reader for Kinvo portfolio files."""

    @staticmethod
    def _parse_brazilian_currency(value: str) -> float:
        """Convert Brazilian currency string to float (e.g., '1.234,56' -> 1234.56)."""
        if pd.isna(value) or value == "":
            return 0.0
        # Remove 'R$', spaces, and convert comma to dot
        cleaned = str(value).replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def read(self) -> pd.DataFrame:
        """
        Read and parse Kinvo portfolio file.

        Returns:
            Standardized portfolio DataFrame
        """
        # Read the Excel file
        df = pd.read_excel(self.file_path)

        # Remove rows with all nulls
        df = df.dropna(how="all")

        # Kinvo has "Produto" instead of ticker, and values as strings
        portfolio_df = pd.DataFrame(
            {
                "ticker": df["Produto"].str.strip(),
                "quantity": 1.0,  # Kinvo doesn't provide quantity for some assets
                "avg_price": df["Valor aplicado"].apply(self._parse_brazilian_currency),
                "current_price": df["Saldo bruto"].apply(
                    self._parse_brazilian_currency
                ),
                "total_value": df["Saldo bruto"].apply(self._parse_brazilian_currency),
                "source": "Kinvo",
                "asset_class": df.get("Classe do Ativo", ""),
                "institution": df.get("Instituição financeira", ""),
            }
        )

        # Remove rows with zero total value
        portfolio_df = portfolio_df[portfolio_df["total_value"] > 0]

        # Remove rows where ticker is null
        portfolio_df = portfolio_df.dropna(subset=["ticker"])

        return self.validate_data(portfolio_df)
