"""Script to compare two portfolio versions and show changes."""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from invest.utils.versioning import PortfolioVersionManager

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def print_header(text: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def print_section(text: str) -> None:
    """Print section separator."""
    print("\n" + "-" * 70)
    print(text)
    print("-" * 70)


def format_currency(value: float) -> str:
    """Format value as Brazilian currency."""
    return f"R$ {value:,.2f}"


def main() -> None:
    """Run version comparison."""
    print_header("📊 Portfolio Version Comparison")

    # Initialize version manager
    vm = PortfolioVersionManager()

    # List available versions
    versions = vm.list_versions()

    if len(versions) < 1:
        print("❌ No portfolio versions found.")
        print("Run 'python main.py' first to create a consolidation.")
        return

    print_section("Available Versions")
    print(f"Total versions: {len(versions)}\n")

    for i, version in enumerate(versions, 1):
        print(f"{i}. {version['date']}")
        print(f"   Assets: {version.get('total_assets', 'N/A')}")
        print(f"   Value: {format_currency(version.get('total_value', 0))}")
        print()

    if len(versions) < 2:
        print("⚠ Need at least 2 versions to compare.")
        print("Run 'python main.py' again with new data to create another version.")
        return

    # Compare last two versions
    print_section("Comparing Versions")

    older = versions[-2]["date"]
    newer = versions[-1]["date"]

    print(f"Comparing: {older} → {newer}\n")

    try:
        comparison = vm.compare_versions(older, newer)

        # Show summary
        print_section("Summary")
        print(f"Date Range: {comparison['date1']} → {comparison['date2']}")
        print(f"\nOld Total Value: {format_currency(comparison['total_value_old'])}")
        print(f"New Total Value: {format_currency(comparison['total_value_new'])}")
        print(f"Change: {format_currency(comparison['total_change'])}")

        change_pct = (
            comparison["total_change"] / comparison["total_value_old"] * 100
            if comparison["total_value_old"] > 0
            else 0
        )
        print(f"Change %: {change_pct:+.2f}%")

        # New assets
        if comparison["new_assets"]:
            print_section(f"New Assets ({len(comparison['new_assets'])})")
            for asset in comparison["new_assets"][:10]:
                print(f"  ✅ {asset}")
            if len(comparison["new_assets"]) > 10:
                print(f"  ... and {len(comparison['new_assets']) - 10} more")

        # Removed assets
        if comparison["removed_assets"]:
            print_section(f"Removed Assets ({len(comparison['removed_assets'])})")
            for asset in comparison["removed_assets"][:10]:
                print(f"  ❌ {asset}")
            if len(comparison["removed_assets"]) > 10:
                print(f"  ... and {len(comparison['removed_assets']) - 10} more")

        # Value changes
        if comparison["value_changes"]:
            print_section("Top Value Changes")
            print(f"{'Asset':<40} {'Old Value':>15} {'New Value':>15} {'Change':>15} {'%':>8}")
            print("-" * 100)

            for change in comparison["value_changes"][:15]:
                ticker = change["ticker"][:38]
                old_val = format_currency(change["old_value"])
                new_val = format_currency(change["new_value"])
                delta = format_currency(change["change"])
                pct = f"{change['change_pct']:+.2f}%"

                # Color code positive/negative
                symbol = "📈" if change["change"] > 0 else "📉"

                print(
                    f"{symbol} {ticker:<38} {old_val:>15} {new_val:>15} "
                    f"{delta:>15} {pct:>8}"
                )

        # Save detailed report
        print_section("Saving Report")
        report_file = vm.generate_change_report(older, newer)
        print(f"✓ Detailed report saved: {report_file}")

        print_header("✅ Comparison Complete!")

    except Exception as e:
        print(f"❌ Error comparing versions: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
