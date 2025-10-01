"""Command-line interface for portfolio analysis."""

import argparse
import subprocess
import sys
from pathlib import Path

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def run_consolidation(args) -> None:
    """Run portfolio consolidation."""
    print("🔄 Running portfolio consolidation...\n")
    subprocess.run([sys.executable, "main.py"])


def run_comparison(args) -> None:
    """Run version comparison."""
    print("📊 Running version comparison...\n")
    subprocess.run([sys.executable, "scripts/compare_versions.py"])


def run_visualizations(args) -> None:
    """Generate visualizations."""
    print("📈 Generating visualizations...\n")
    subprocess.run([sys.executable, "scripts/visualize_portfolio.py"])


def run_report(args) -> None:
    """Generate detailed report."""
    print("📄 Generating detailed report...\n")
    subprocess.run([sys.executable, "scripts/generate_report.py"])


def run_explore(args) -> None:
    """Explore spreadsheet structures."""
    print("🔍 Exploring spreadsheets...\n")
    subprocess.run([sys.executable, "scripts/explore_sheets.py"])


def run_test(args) -> None:
    """Test readers."""
    print("🧪 Testing readers...\n")
    subprocess.run([sys.executable, "scripts/test_readers.py"])


def run_all(args) -> None:
    """Run complete analysis pipeline."""
    print("🚀 Running complete analysis pipeline...\n")
    print("=" * 70 + "\n")

    # 1. Consolidation
    print("Step 1/4: Consolidating portfolios...")
    subprocess.run([sys.executable, "main.py"])
    print()

    # 2. Visualizations
    print("Step 2/4: Generating visualizations...")
    subprocess.run([sys.executable, "scripts/visualize_portfolio.py"])
    print()

    # 3. Report
    print("Step 3/4: Generating detailed report...")
    subprocess.run([sys.executable, "scripts/generate_report.py"])
    print()

    # 4. Comparison (if multiple versions exist)
    print("Step 4/4: Comparing versions...")
    subprocess.run([sys.executable, "scripts/compare_versions.py"])
    print()

    print("=" * 70)
    print("✅ Complete analysis pipeline finished!")
    print("\nGenerated outputs:")
    print("  📊 output/consolidated_portfolio.csv")
    print("  📈 output/visualizations/*.png")
    print("  📄 output/detailed_report.txt")
    print("  📉 output/reports/changes_*.json")


def list_outputs(args) -> None:
    """List all generated outputs."""
    print("📂 Generated Outputs\n")
    print("=" * 70 + "\n")

    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ No outputs found. Run consolidation first.")
        return

    # Consolidated files
    print("Consolidated Portfolios:")
    for file in sorted(output_dir.glob("consolidated_portfolio.csv")):
        size = file.stat().st_size / 1024
        print(f"  ✓ {file} ({size:.1f} KB)")

    csv_dir = output_dir / "consolidated"
    if csv_dir.exists():
        for file in sorted(csv_dir.glob("*.csv")):
            size = file.stat().st_size / 1024
            print(f"  ✓ {file} ({size:.1f} KB)")

    # Visualizations
    print("\nVisualizations:")
    viz_dir = output_dir / "visualizations"
    if viz_dir.exists():
        for file in sorted(viz_dir.glob("*.png")):
            size = file.stat().st_size / 1024
            print(f"  ✓ {file.name} ({size:.1f} KB)")
    else:
        print("  (none generated yet)")

    # Reports
    print("\nReports:")
    for file in sorted(output_dir.glob("*.txt")):
        size = file.stat().st_size / 1024
        print(f"  ✓ {file.name} ({size:.1f} KB)")

    for file in sorted(output_dir.glob("*.json")):
        size = file.stat().st_size / 1024
        print(f"  ✓ {file.name} ({size:.1f} KB)")

    reports_dir = output_dir / "reports"
    if reports_dir.exists():
        for file in sorted(reports_dir.glob("*.json")):
            size = file.stat().st_size / 1024
            print(f"  ✓ reports/{file.name} ({size:.1f} KB)")

    # Snapshots
    print("\nSnapshots:")
    data_dir = Path("data/raw")
    if data_dir.exists():
        snapshots = sorted(data_dir.glob("*"))
        if snapshots:
            for snapshot in snapshots:
                files = list(snapshot.glob("*"))
                print(f"  ✓ {snapshot.name} ({len(files)} files)")
        else:
            print("  (none created yet)")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Investment Portfolio Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s consolidate          Run portfolio consolidation
  %(prog)s all                  Run complete analysis pipeline
  %(prog)s visualize            Generate charts and graphs
  %(prog)s report               Generate detailed text report
  %(prog)s compare              Compare portfolio versions
  %(prog)s list                 List all generated outputs
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Consolidate command
    consolidate_parser = subparsers.add_parser(
        "consolidate", help="Consolidate portfolios from all sources"
    )
    consolidate_parser.set_defaults(func=run_consolidation)

    # Compare command
    compare_parser = subparsers.add_parser(
        "compare", help="Compare portfolio versions"
    )
    compare_parser.set_defaults(func=run_comparison)

    # Visualize command
    viz_parser = subparsers.add_parser(
        "visualize", help="Generate visualizations"
    )
    viz_parser.set_defaults(func=run_visualizations)

    # Report command
    report_parser = subparsers.add_parser(
        "report", help="Generate detailed report"
    )
    report_parser.set_defaults(func=run_report)

    # Explore command
    explore_parser = subparsers.add_parser(
        "explore", help="Explore spreadsheet structures"
    )
    explore_parser.set_defaults(func=run_explore)

    # Test command
    test_parser = subparsers.add_parser("test", help="Test portfolio readers")
    test_parser.set_defaults(func=run_test)

    # All command
    all_parser = subparsers.add_parser(
        "all", help="Run complete analysis pipeline"
    )
    all_parser.set_defaults(func=run_all)

    # List command
    list_parser = subparsers.add_parser("list", help="List generated outputs")
    list_parser.set_defaults(func=list_outputs)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # Run the selected command
    args.func(args)


if __name__ == "__main__":
    main()
