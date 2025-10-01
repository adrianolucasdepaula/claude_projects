"""XP Investimentos brokerage portfolio reader."""

import pandas as pd

from .base import BasePortfolioReader


class XPReader(BasePortfolioReader):
    """Reader for XP brokerage portfolio files."""

    @staticmethod
    def _parse_brazilian_currency(value: str) -> float:
        """Convert Brazilian currency string to float (e.g., 'R$ 1.234,56' -> 1234.56)."""
        if pd.isna(value) or value == "" or value == " ":
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
        Read and parse XP portfolio file.

        XP files have a hierarchical structure with categories and repeated headers.
        We need to identify data rows and extract relevant information.

        Returns:
            Standardized portfolio DataFrame
        """
        # Read the Excel file
        df = pd.read_excel(self.file_path)

        # Find rows that look like asset data (not headers, not categories)
        # Asset rows typically have values in the second column (Posição/Valor)
        assets = []
        current_category = ""

        for idx, row in df.iterrows():
            first_col = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            second_col = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""

            # Skip empty rows
            if not first_col or first_col == " ":
                continue

            # Detect category headers (e.g., "Fundos de Investimentos")
            if pd.isna(row.iloc[1]) or row.iloc[1] == " ":
                if "%" not in first_col:  # Not a percentage header
                    current_category = first_col
                continue

            # Detect column headers
            if any(
                header in first_col.lower() or header in second_col.lower()
                for header in ["posição", "valor", "% alocação"]
            ):
                continue

            # This looks like an asset row
            if second_col.startswith("R$") or "." in second_col or "," in second_col:
                # Skip if first column also looks like currency (it's a summary row)
                if first_col.startswith("R$"):
                    continue

                try:
                    ticker = first_col
                    total_value = self._parse_brazilian_currency(second_col)

                    # Try to get invested value from column 6 (index 5)
                    invested_value = 0.0
                    if len(row) > 5:
                        invested_value = self._parse_brazilian_currency(row.iloc[5])

                    if total_value > 0:
                        assets.append(
                            {
                                "ticker": ticker,
                                "quantity": 1.0,  # XP doesn't provide quantity
                                "avg_price": invested_value,
                                "current_price": total_value,
                                "total_value": total_value,
                                "source": "XP",
                                "category": current_category,
                            }
                        )
                except Exception:
                    # Skip rows that can't be parsed
                    continue

        # Create DataFrame from parsed assets
        if not assets:
            # Return empty but valid DataFrame
            portfolio_df = pd.DataFrame(
                columns=[
                    "ticker",
                    "quantity",
                    "avg_price",
                    "current_price",
                    "total_value",
                    "source",
                ]
            )
        else:
            portfolio_df = pd.DataFrame(assets)

        return self.validate_data(portfolio_df)
