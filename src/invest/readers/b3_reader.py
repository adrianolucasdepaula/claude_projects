"""B3 (Brazilian Stock Exchange) portfolio reader."""

import pandas as pd

from .base import BasePortfolioReader


class B3Reader(BasePortfolioReader):
    """Reader for B3 portfolio files."""

    def read(self) -> pd.DataFrame:
        """
        Read and parse B3 portfolio file.

        Returns:
            Standardized portfolio DataFrame
        """
        # Read the Excel file
        df = pd.read_excel(self.file_path)

        # Remove rows with all nulls
        df = df.dropna(how="all")

        # Map B3 columns to standardized format
        portfolio_df = pd.DataFrame(
            {
                "ticker": df["Código de Negociação"].str.strip(),
                "quantity": pd.to_numeric(df["Quantidade"], errors="coerce"),
                "avg_price": 0.0,  # B3 doesn't provide average price
                "current_price": pd.to_numeric(
                    df["Preço de Fechamento"], errors="coerce"
                ),
                "total_value": pd.to_numeric(df["Valor Atualizado"], errors="coerce"),
                "source": "B3",
                "institution": df.get("Instituição", "").str.strip()
                if "Instituição" in df.columns
                else "",
                "asset_type": df.get("Tipo", "")
                if "Tipo" in df.columns
                else "",
            }
        )

        # Remove rows where ticker is null
        portfolio_df = portfolio_df.dropna(subset=["ticker"])

        # Calculate avg_price from total_value and quantity
        portfolio_df.loc[portfolio_df["quantity"] > 0, "avg_price"] = (
            portfolio_df["total_value"] / portfolio_df["quantity"]
        )

        return self.validate_data(portfolio_df)
