"""Script to explore and analyze the structure of all portfolio spreadsheets."""

import json
import sys
from pathlib import Path

import pandas as pd

# Fix encoding issues on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def analyze_spreadsheet(file_path: Path) -> dict:
    """
    Analyze a single spreadsheet and extract its structure.

    Args:
        file_path: Path to the spreadsheet file

    Returns:
        Dictionary with analysis results
    """
    try:
        # Read the spreadsheet
        # For .xls files, check if it's actually HTML
        if file_path.suffix == ".xls":
            # Read first bytes to detect format
            with open(file_path, "rb") as f:
                first_bytes = f.read(10)

            if first_bytes.startswith(b"<html") or first_bytes.startswith(b"<!DOC"):
                # It's HTML disguised as XLS (common in old Excel exports)
                df = pd.read_html(file_path)[0]  # Read first table
            else:
                df = pd.read_excel(file_path, engine="xlrd")
        else:
            df = pd.read_excel(file_path)

        # Get basic info
        analysis = {
            "file": file_path.name,
            "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_data": df.head(3).to_dict("records"),
            "null_counts": df.isnull().sum().to_dict(),
            "unique_values": {},
        }

        # Get unique value counts for small columns
        for col in df.columns:
            if df[col].dtype == "object" and df[col].nunique() < 50:
                analysis["unique_values"][col] = int(df[col].nunique())

        # Add statistics for numeric columns
        numeric_stats = {}
        for col in df.select_dtypes(include=["number"]).columns:
            numeric_stats[col] = {
                "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
            }
        analysis["numeric_stats"] = numeric_stats

        return {"success": True, "data": analysis}

    except Exception as e:
        return {"success": False, "error": str(e), "file": file_path.name}


def main() -> None:
    """Main function to analyze all spreadsheets."""
    # Find all spreadsheet files
    planilhas_dir = Path("planilhas")
    spreadsheet_files = list(planilhas_dir.glob("*.xlsx")) + list(
        planilhas_dir.glob("*.xls")
    )

    if not spreadsheet_files:
        print("❌ No spreadsheet files found in 'planilhas/' directory")
        return

    print(f"📊 Found {len(spreadsheet_files)} spreadsheet(s) to analyze\n")
    print("=" * 80)

    results = {}
    for file_path in sorted(spreadsheet_files):
        print(f"\n📄 Analyzing: {file_path.name}")
        print("-" * 80)

        result = analyze_spreadsheet(file_path)

        if result["success"]:
            data = result["data"]
            results[file_path.stem] = data

            print(f"✅ Successfully analyzed")
            print(f"   Shape: {data['shape']['rows']} rows × {data['shape']['columns']} columns")
            print(f"   Columns: {', '.join(data['columns'])}")

            # Show sample data
            print(f"\n   Sample data (first 3 rows):")
            for i, row in enumerate(data["sample_data"], 1):
                print(f"   Row {i}: {row}")

            # Show data types
            print(f"\n   Data types:")
            for col, dtype in data["dtypes"].items():
                null_count = data["null_counts"].get(col, 0)
                null_info = f" ({null_count} nulls)" if null_count > 0 else ""
                print(f"      {col}: {dtype}{null_info}")

        else:
            print(f"❌ Error: {result['error']}")
            results[file_path.stem] = {"error": result["error"]}

    # Save results to JSON
    output_file = Path("output") / "spreadsheet_analysis.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"✅ Analysis complete! Results saved to: {output_file}")
    print("\n💡 Next steps:")
    print("   1. Review the analysis output above")
    print("   2. Check the JSON file for detailed structure")
    print("   3. Update the reader classes with correct column mappings")


if __name__ == "__main__":
    main()
