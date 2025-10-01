"""Main CLI for investment portfolio analysis with deduplication and versioning."""

import json
import sys
from datetime import datetime
from pathlib import Path

from src.invest.analyzers.portfolio import PortfolioConsolidator
from src.invest.utils.versioning import PortfolioVersionManager

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def print_section(text: str) -> None:
    """Print a section separator."""
    print("\n" + "-" * 70)
    print(text)
    print("-" * 70)


def load_portfolios(consolidator: PortfolioConsolidator, planilhas_dir: Path) -> int:
    """
    Load all portfolio files.

    Args:
        consolidator: Portfolio consolidator instance
        planilhas_dir: Directory containing portfolio files

    Returns:
        Number of successfully loaded portfolios
    """
    sources = {
        "B3": "b3_carrteira.xlsx",
        "Kinvo": "kinvo_carteira.xlsx",
        "MyProfit": "myprofit_carteira.xls",
        "XP": "xp_carteira.xlsx",
    }

    loaded_count = 0
    print_section("Loading Portfolio Data")

    for source_name, filename in sources.items():
        file_path = planilhas_dir / filename
        if not file_path.exists():
            print(f"⚠ Skipping {source_name}: File not found ({filename})")
            continue

        try:
            if source_name == "B3":
                consolidator.add_b3(file_path)
            elif source_name == "Kinvo":
                consolidator.add_kinvo(file_path)
            elif source_name == "MyProfit":
                consolidator.add_myprofit(file_path)
            elif source_name == "XP":
                consolidator.add_xp(file_path)

            print(f"✓ Loaded {source_name} portfolio from {filename}")
            loaded_count += 1
        except Exception as e:
            print(f"✗ Error loading {source_name} portfolio: {e}")

    return loaded_count


def show_summary(consolidator: PortfolioConsolidator, consolidated_df) -> None:
    """Display portfolio summary."""
    print_section("Portfolio Summary")

    summary = consolidator.summary(consolidated_df)

    print(f"Total Assets: {summary['total_positions']}")
    print(f"Total Invested: R$ {summary['total_invested']:,.2f}")
    print(f"Current Value: R$ {summary['total_value']:,.2f}")
    print(f"Total P/L: R$ {summary['total_profit_loss']:,.2f}")
    print(f"Total P/L %: {summary['total_profit_loss_pct']:.2f}%")
    print(f"\nData Sources: {', '.join(summary['sources'])}")

    print("\n📈 Top 5 Holdings:")
    for i, holding in enumerate(summary["top_holdings"], 1):
        print(
            f"  {i}. {holding['ticker']:<40} "
            f"R$ {holding['total_value']:>12,.2f}  "
            f"({holding['profit_loss_pct']:>6.2f}%)  "
            f"[{holding['source']}]"
        )


def show_duplicates(consolidator: PortfolioConsolidator) -> None:
    """Display duplicate assets report."""
    print_section("Duplicate Assets Analysis")

    duplicates = consolidator.find_duplicates()

    if duplicates.empty:
        print("✓ No duplicate assets found across sources")
        return

    print(f"Found {len(duplicates)} assets appearing in multiple sources:\n")

    for _, dup in duplicates.iterrows():
        print(f"📊 {dup['ticker']} (normalized: {dup['normalized']})")
        print(f"   Sources: {dup['sources']} ({dup['count']} occurrences)")
        print(f"   Combined value: R$ {dup['total_value_sum']:,.2f}")
        for val_source in dup["values_by_source"]:
            print(f"      - {val_source['source']}: R$ {val_source['total_value']:,.2f}")
        print()


def main() -> None:
    """Run the portfolio consolidation CLI."""
    print_header("📊 Investment Portfolio Consolidation System")

    print("Deduplication Strategy: AGGREGATE (sum quantities from all sources)")
    print("Versioning: ENABLED (snapshots will be saved)\n")

    # Initialize consolidator with deduplication and versioning
    consolidator = PortfolioConsolidator(
        deduplication_strategy="aggregate",
        enable_versioning=True,
        base_dir=".",
    )

    # Define portfolio files directory
    planilhas_dir = Path("planilhas")

    # Load portfolios
    loaded_count = load_portfolios(consolidator, planilhas_dir)

    if loaded_count == 0:
        print("\n❌ No portfolio data loaded. Exiting.")
        return

    print(f"\n✓ Successfully loaded {loaded_count} portfolio source(s)")

    # Show duplicate analysis
    show_duplicates(consolidator)

    # Consolidate with deduplication
    print_section("Consolidating Portfolios")
    print("Applying deduplication strategy: AGGREGATE")
    print("Removing duplicate assets and combining values...")

    consolidated = consolidator.consolidate(save=True)

    print(f"\n✓ Consolidation complete!")
    print(f"   Total unique assets after deduplication: {len(consolidated)}")

    # Show summary
    show_summary(consolidator, consolidated)

    # Save outputs
    print_section("Saving Results")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Save consolidated CSV
    csv_file = output_dir / "consolidated_portfolio.csv"
    consolidated.to_csv(csv_file, index=False, encoding="utf-8")
    print(f"✓ Consolidated portfolio saved: {csv_file}")

    # Save summary JSON
    summary_file = output_dir / "summary.json"
    summary = consolidator.summary(consolidated)
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"✓ Summary statistics saved: {summary_file}")

    # Show versioning info
    print_section("Versioning Information")
    version_manager = consolidator.version_manager
    if version_manager:
        versions = version_manager.list_versions()
        print(f"Total snapshots: {len(versions)}")
        if versions:
            latest = versions[-1]
            print(f"Latest snapshot: {latest['date']}")
            print(f"   - Assets: {latest.get('total_assets', 'N/A')}")
            print(f"   - Value: R$ {latest.get('total_value', 0):,.2f}")

        print(f"\nSnapshot location: {version_manager.raw_dir}")
        print(f"Consolidated versions: {version_manager.consolidated_dir}")

    print_header("✅ Portfolio Consolidation Complete!")
    print("Next steps:")
    print("  - Review the consolidated portfolio in output/consolidated_portfolio.csv")
    print("  - Check the summary in output/summary.json")
    print("  - Compare with previous versions using the versioning system")


if __name__ == "__main__":
    main()
