"""Deduplication utilities for portfolio consolidation."""

from typing import Literal

import pandas as pd


class PortfolioDeduplicator:
    """Handle deduplication of portfolio assets from multiple sources."""

    STRATEGY_AGGREGATE = "aggregate"  # Sum quantities from all sources
    STRATEGY_PRIORITIZE = "prioritize"  # Keep data from highest priority source
    STRATEGY_LATEST = "latest"  # Keep most recent data

    # Source priority (higher number = higher priority)
    SOURCE_PRIORITY = {
        "MyProfit": 4,  # Most complete data
        "B3": 3,  # Official exchange data
        "XP": 2,  # Brokerage data
        "Kinvo": 1,  # Aggregator platform
    }

    def __init__(
        self,
        strategy: Literal["aggregate", "prioritize", "latest"] = "aggregate",
    ) -> None:
        """
        Initialize the deduplicator.

        Args:
            strategy: Deduplication strategy to use
        """
        self.strategy = strategy

    def _normalize_ticker(self, ticker: str) -> str:
        """
        Normalize ticker for comparison.

        Args:
            ticker: Ticker symbol

        Returns:
            Normalized ticker
        """
        # Remove extra spaces, convert to uppercase
        normalized = str(ticker).strip().upper()

        # Some normalizations for Brazilian market
        # Tesouro Direto titles often have different formats
        if "TESOURO" in normalized:
            # Keep only the main part
            if "SELIC" in normalized:
                # Extract year if present
                import re
                match = re.search(r"20\d{2}", normalized)
                if match:
                    return f"TESOURO SELIC {match.group()}"
                return "TESOURO SELIC"
            elif "IPCA" in normalized:
                import re
                match = re.search(r"20\d{2}", normalized)
                if match:
                    return f"TESOURO IPCA {match.group()}"
                return "TESOURO IPCA"

        return normalized

    def deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Deduplicate portfolio DataFrame.

        Args:
            df: Portfolio DataFrame with potential duplicates

        Returns:
            Deduplicated DataFrame
        """
        if df.empty:
            return df

        # Add normalized ticker for matching
        df = df.copy()
        df["_normalized_ticker"] = df["ticker"].apply(self._normalize_ticker)

        if self.strategy == self.STRATEGY_AGGREGATE:
            return self._aggregate_duplicates(df)
        elif self.strategy == self.STRATEGY_PRIORITIZE:
            return self._prioritize_by_source(df)
        elif self.strategy == self.STRATEGY_LATEST:
            # For now, same as prioritize (would need timestamps for true latest)
            return self._prioritize_by_source(df)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def _aggregate_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate duplicate assets by summing quantities and values.

        Args:
            df: DataFrame with potential duplicates

        Returns:
            Aggregated DataFrame
        """
        # Group by normalized ticker
        grouped = df.groupby("_normalized_ticker")

        aggregated_data = []
        for normalized_ticker, group in grouped:
            # If only one source, keep as is
            if len(group) == 1:
                row_dict = group.iloc[0].to_dict()
                # Remove the normalized ticker
                row_dict.pop("_normalized_ticker", None)
                aggregated_data.append(row_dict)
                continue

            # Multiple sources - aggregate
            total_quantity = group["quantity"].sum()
            total_value = group["total_value"].sum()

            # Weighted average of prices
            avg_price = (
                (group["avg_price"] * group["quantity"]).sum() / total_quantity
                if total_quantity > 0
                else group["avg_price"].mean()
            )

            current_price = (
                total_value / total_quantity if total_quantity > 0 else
                group["current_price"].mean()
            )

            # Use the original ticker from the highest priority source
            best_source_idx = group["source"].map(self.SOURCE_PRIORITY).idxmax()
            original_ticker = group.loc[best_source_idx, "ticker"]

            # Combine sources
            sources = ", ".join(sorted(group["source"].unique()))

            # Create aggregated row
            agg_row = {
                "ticker": original_ticker,
                "quantity": total_quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "total_value": total_value,
                "source": sources,
                "_normalized_ticker": normalized_ticker,
            }

            # Add optional columns if present
            for col in ["institution", "asset_type", "asset_class", "category"]:
                if col in group.columns:
                    # Take from highest priority source
                    value = group.loc[best_source_idx, col]
                    # Convert to string if it's not a simple type
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    agg_row[col] = value

            aggregated_data.append(agg_row)

        result = pd.DataFrame(aggregated_data)

        # Remove the normalized ticker column
        result = result.drop(columns=["_normalized_ticker"])

        return result

    def _prioritize_by_source(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Keep only data from the highest priority source for each asset.

        Args:
            df: DataFrame with potential duplicates

        Returns:
            Deduplicated DataFrame with highest priority source
        """
        # Add priority column
        df = df.copy()
        df["_priority"] = df["source"].map(
            lambda x: max(
                [self.SOURCE_PRIORITY.get(s.strip(), 0) for s in x.split(",")]
            )
        )

        # For each normalized ticker, keep only the highest priority
        df = df.sort_values("_priority", ascending=False)
        df = df.drop_duplicates(subset=["_normalized_ticker"], keep="first")

        # Remove temporary columns
        df = df.drop(columns=["_normalized_ticker", "_priority"])

        return df

    def find_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find and report duplicate assets across sources.

        Args:
            df: Portfolio DataFrame

        Returns:
            DataFrame with duplicate assets and their sources
        """
        df = df.copy()
        df["_normalized_ticker"] = df["ticker"].apply(self._normalize_ticker)

        # Find tickers that appear in multiple sources
        ticker_counts = df.groupby("_normalized_ticker").size()
        duplicated_tickers = ticker_counts[ticker_counts > 1].index

        if len(duplicated_tickers) == 0:
            return pd.DataFrame(
                columns=["ticker", "sources", "count", "total_value_sum"]
            )

        # Create report
        duplicate_report = []
        for norm_ticker in duplicated_tickers:
            group = df[df["_normalized_ticker"] == norm_ticker]
            duplicate_report.append(
                {
                    "ticker": group.iloc[0]["ticker"],
                    "normalized": norm_ticker,
                    "sources": ", ".join(sorted(group["source"].unique())),
                    "count": len(group),
                    "total_value_sum": group["total_value"].sum(),
                    "values_by_source": group[["source", "total_value"]]
                    .to_dict("records"),
                }
            )

        return pd.DataFrame(duplicate_report)
