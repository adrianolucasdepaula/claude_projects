"""Test script for portfolio readers."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from invest.readers.b3_reader import B3Reader
from invest.readers.kinvo_reader import KinvoReader
from invest.readers.myprofit_reader import MyProfitReader
from invest.readers.xp_reader import XPReader

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def test_reader(name: str, reader_class, file_path: str) -> None:
    """Test a single reader."""
    print(f"=== {name} Reader ===")
    try:
        reader = reader_class(file_path)
        df = reader.read()
        print(f"✓ Success: {len(df)} assets loaded")
        print(f"  Total value: R$ {df['total_value'].sum():,.2f}")
        if len(df) > 0:
            print(f"  Sample tickers: {df['ticker'].head(3).tolist()}")
            print(f"  Columns: {list(df.columns)}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    print()


def main() -> None:
    """Run all reader tests."""
    print("Testing Portfolio Readers\n")
    print("=" * 60 + "\n")

    test_reader("B3", B3Reader, "planilhas/b3_carrteira.xlsx")
    test_reader("Kinvo", KinvoReader, "planilhas/kinvo_carteira.xlsx")
    test_reader("MyProfit", MyProfitReader, "planilhas/myprofit_carteira.xls")
    test_reader("XP", XPReader, "planilhas/xp_carteira.xlsx")

    print("=" * 60)
    print("Testing complete!")


if __name__ == "__main__":
    main()
