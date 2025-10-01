"""Versioning and historical tracking for portfolio consolidations."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


class PortfolioVersionManager:
    """Manage versioned portfolio snapshots and historical data."""

    def __init__(self, base_dir: Path | str = ".") -> None:
        """
        Initialize the version manager.

        Args:
            base_dir: Base directory for the project
        """
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.output_dir = self.base_dir / "output"
        self.raw_dir = self.data_dir / "raw"
        self.consolidated_dir = self.output_dir / "consolidated"
        self.reports_dir = self.output_dir / "reports"

        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.consolidated_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(
        self,
        source_files: dict[str, Path],
        date: datetime | None = None,
    ) -> Path:
        """
        Create a snapshot of source files for a specific date.

        Args:
            source_files: Dictionary mapping source name to file path
            date: Snapshot date (default: today)

        Returns:
            Path to the snapshot directory
        """
        if date is None:
            date = datetime.now()

        # Create snapshot directory
        snapshot_date = date.strftime("%Y-%m-%d")
        snapshot_dir = self.raw_dir / snapshot_date
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Copy files to snapshot
        for source_name, source_path in source_files.items():
            if Path(source_path).exists():
                dest_path = snapshot_dir / Path(source_path).name
                shutil.copy2(source_path, dest_path)

        # Create metadata
        metadata = {
            "date": snapshot_date,
            "timestamp": date.isoformat(),
            "sources": {
                name: str(path.name) for name, path in source_files.items()
            },
        }

        metadata_path = snapshot_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return snapshot_dir

    def save_consolidation(
        self,
        consolidated_df: pd.DataFrame,
        date: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """
        Save a consolidated portfolio with versioning.

        Args:
            consolidated_df: Consolidated portfolio DataFrame
            date: Consolidation date (default: today)
            metadata: Additional metadata to save

        Returns:
            Path to the saved consolidation file
        """
        if date is None:
            date = datetime.now()

        snapshot_date = date.strftime("%Y-%m-%d")

        # Save dated version
        dated_file = self.consolidated_dir / f"portfolio_{snapshot_date}.csv"
        consolidated_df.to_csv(dated_file, index=False, encoding="utf-8")

        # Update 'latest' link
        latest_file = self.consolidated_dir / "latest.csv"
        consolidated_df.to_csv(latest_file, index=False, encoding="utf-8")

        # Save metadata
        if metadata:
            metadata_file = self.consolidated_dir / f"portfolio_{snapshot_date}_meta.json"
            full_metadata = {
                "date": snapshot_date,
                "timestamp": date.isoformat(),
                "total_assets": len(consolidated_df),
                "total_value": float(consolidated_df["total_value"].sum()),
                **metadata,
            }
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(full_metadata, f, indent=2, ensure_ascii=False)

        return dated_file

    def compare_versions(
        self,
        date1: str | datetime,
        date2: str | datetime | None = None,
    ) -> dict[str, Any]:
        """
        Compare two portfolio versions.

        Args:
            date1: First date (older)
            date2: Second date (newer, default: latest)

        Returns:
            Dictionary with comparison results
        """
        # Parse dates
        if isinstance(date1, str):
            date1_str = date1
        else:
            date1_str = date1.strftime("%Y-%m-%d")

        if date2 is None:
            file2 = self.consolidated_dir / "latest.csv"
            date2_str = "latest"
        elif isinstance(date2, str):
            date2_str = date2
            file2 = self.consolidated_dir / f"portfolio_{date2_str}.csv"
        else:
            date2_str = date2.strftime("%Y-%m-%d")
            file2 = self.consolidated_dir / f"portfolio_{date2_str}.csv"

        file1 = self.consolidated_dir / f"portfolio_{date1_str}.csv"

        # Load both versions
        if not file1.exists():
            raise FileNotFoundError(f"Portfolio for {date1_str} not found")
        if not file2.exists():
            raise FileNotFoundError(f"Portfolio for {date2_str} not found")

        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)

        # Find changes
        tickers1 = set(df1["ticker"])
        tickers2 = set(df2["ticker"])

        new_assets = tickers2 - tickers1
        removed_assets = tickers1 - tickers2
        common_assets = tickers1 & tickers2

        # Calculate value changes for common assets
        value_changes = []
        for ticker in common_assets:
            val1 = df1[df1["ticker"] == ticker]["total_value"].iloc[0]
            val2 = df2[df2["ticker"] == ticker]["total_value"].iloc[0]
            change = val2 - val1
            change_pct = (change / val1 * 100) if val1 > 0 else 0

            if abs(change) > 0.01:  # Only significant changes
                value_changes.append(
                    {
                        "ticker": ticker,
                        "old_value": val1,
                        "new_value": val2,
                        "change": change,
                        "change_pct": change_pct,
                    }
                )

        # Sort by absolute change
        value_changes.sort(key=lambda x: abs(x["change"]), reverse=True)

        comparison = {
            "date1": date1_str,
            "date2": date2_str,
            "total_value_old": float(df1["total_value"].sum()),
            "total_value_new": float(df2["total_value"].sum()),
            "total_change": float(df2["total_value"].sum() - df1["total_value"].sum()),
            "new_assets": sorted(list(new_assets)),
            "removed_assets": sorted(list(removed_assets)),
            "value_changes": value_changes[:20],  # Top 20 changes
        }

        return comparison

    def generate_change_report(
        self,
        date1: str | datetime,
        date2: str | datetime | None = None,
    ) -> Path:
        """
        Generate a detailed change report between two versions.

        Args:
            date1: First date (older)
            date2: Second date (newer, default: latest)

        Returns:
            Path to the generated report
        """
        comparison = self.compare_versions(date1, date2)

        # Generate report filename
        if comparison["date2"] == "latest":
            report_file = self.reports_dir / f"changes_{comparison['date1']}_to_latest.json"
        else:
            report_file = (
                self.reports_dir
                / f"changes_{comparison['date1']}_to_{comparison['date2']}.json"
            )

        # Save report
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)

        return report_file

    def list_versions(self) -> list[dict[str, Any]]:
        """
        List all available portfolio versions.

        Returns:
            List of version information dictionaries
        """
        versions = []

        for file_path in sorted(self.consolidated_dir.glob("portfolio_*.csv")):
            if file_path.name == "latest.csv":
                continue

            # Extract date from filename
            date_str = file_path.stem.replace("portfolio_", "")

            # Try to load metadata
            meta_file = self.consolidated_dir / f"{file_path.stem}_meta.json"
            if meta_file.exists():
                with open(meta_file, encoding="utf-8") as f:
                    metadata = json.load(f)
            else:
                # Load CSV to get basic info
                df = pd.read_csv(file_path)
                metadata = {
                    "total_assets": len(df),
                    "total_value": float(df["total_value"].sum()),
                }

            versions.append(
                {
                    "date": date_str,
                    "file": str(file_path),
                    **metadata,
                }
            )

        return versions
