"""Portfolio consolidation and analysis."""

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from ..readers.b3_reader import B3Reader
from ..readers.kinvo_reader import KinvoReader
from ..readers.myprofit_reader import MyProfitReader
from ..readers.xp_reader import XPReader
from ..utils.deduplication import PortfolioDeduplicator
from ..utils.versioning import PortfolioVersionManager


class PortfolioConsolidator:
    """Consolidate portfolios from multiple sources with deduplication and versioning."""

    def __init__(
        self,
        deduplication_strategy: Literal["aggregate", "prioritize", "latest"] = "aggregate",
        enable_versioning: bool = True,
        base_dir: Path | str = ".",
    ) -> None:
        """
        Initialize the portfolio consolidator.

        Args:
            deduplication_strategy: Strategy for handling duplicate assets
            enable_versioning: Whether to enable versioning of consolidations
            base_dir: Base directory for versioning
        """
        self.portfolios: list[pd.DataFrame] = []
        self.source_files: dict[str, Path] = {}
        self.deduplicator = PortfolioDeduplicator(strategy=deduplication_strategy)
        self.enable_versioning = enable_versioning
        self.version_manager = (
            PortfolioVersionManager(base_dir) if enable_versioning else None
        )

    def add_b3(self, file_path: str | Path) -> None:
        """Add B3 portfolio."""
        file_path = Path(file_path)
        reader = B3Reader(file_path)
        self.portfolios.append(reader.read())
        self.source_files["B3"] = file_path

    def add_kinvo(self, file_path: str | Path) -> None:
        """Add Kinvo portfolio."""
        file_path = Path(file_path)
        reader = KinvoReader(file_path)
        self.portfolios.append(reader.read())
        self.source_files["Kinvo"] = file_path

    def add_myprofit(self, file_path: str | Path) -> None:
        """Add MyProfit portfolio."""
        file_path = Path(file_path)
        reader = MyProfitReader(file_path)
        self.portfolios.append(reader.read())
        self.source_files["MyProfit"] = file_path

    def add_xp(self, file_path: str | Path) -> None:
        """Add XP portfolio."""
        file_path = Path(file_path)
        reader = XPReader(file_path)
        self.portfolios.append(reader.read())
        self.source_files["XP"] = file_path

    def consolidate(self, save: bool = False, date: datetime | None = None) -> pd.DataFrame:
        """
        Consolidate all portfolios with deduplication.

        Args:
            save: Whether to save the consolidation with versioning
            date: Date for the consolidation (default: today)

        Returns:
            Consolidated portfolio DataFrame
        """
        if not self.portfolios:
            return pd.DataFrame()

        # Combine all portfolios
        combined = pd.concat(self.portfolios, ignore_index=True)

        # Apply deduplication
        consolidated = self.deduplicator.deduplicate(combined)

        # Calculate additional metrics
        consolidated["profit_loss"] = (
            consolidated["current_price"] - consolidated["avg_price"]
        ) * consolidated["quantity"]

        # Handle division by zero for profit_loss_pct
        consolidated["profit_loss_pct"] = 0.0
        mask = consolidated["avg_price"] > 0
        consolidated.loc[mask, "profit_loss_pct"] = (
            (consolidated.loc[mask, "current_price"] - consolidated.loc[mask, "avg_price"])
            / consolidated.loc[mask, "avg_price"]
            * 100
        )

        # Sort by total value descending
        consolidated = consolidated.sort_values("total_value", ascending=False)

        # Save if requested and versioning is enabled
        if save and self.enable_versioning and self.version_manager:
            # Create snapshot of source files
            self.version_manager.create_snapshot(self.source_files, date)

            # Save consolidation
            metadata = {
                "sources": list(self.source_files.keys()),
                "deduplication_strategy": self.deduplicator.strategy,
                "total_sources": len(self.portfolios),
            }
            self.version_manager.save_consolidation(consolidated, date, metadata)

        return consolidated

    def find_duplicates(self) -> pd.DataFrame:
        """
        Find and report duplicate assets across sources.

        Returns:
            DataFrame with duplicate information
        """
        if not self.portfolios:
            return pd.DataFrame()

        combined = pd.concat(self.portfolios, ignore_index=True)
        return self.deduplicator.find_duplicates(combined)

    def summary(self, consolidated: pd.DataFrame | None = None) -> dict[str, Any]:
        """
        Generate portfolio summary statistics.

        Args:
            consolidated: Pre-consolidated DataFrame (optional)

        Returns:
            Dictionary with summary statistics
        """
        if consolidated is None:
            consolidated = self.consolidate()

        if consolidated.empty:
            return {}

        total_value = consolidated["total_value"].sum()
        total_profit_loss = consolidated["profit_loss"].sum()

        # Calculate invested value (from avg_price * quantity)
        total_invested = (consolidated["avg_price"] * consolidated["quantity"]).sum()

        return {
            "total_positions": len(consolidated),
            "total_value": float(total_value),
            "total_invested": float(total_invested),
            "total_profit_loss": float(total_profit_loss),
            "total_profit_loss_pct": float(
                (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
            ),
            "sources": list(set(
                source for sources in consolidated["source"].unique()
                for source in sources.split(", ")
            )),
            "top_holdings": consolidated.nlargest(5, "total_value")[
                ["ticker", "total_value", "profit_loss_pct", "source"]
            ].to_dict("records"),
        }
