"""Configuration file for portfolio analysis system."""

from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent
PLANILHAS_DIR = BASE_DIR / "planilhas"
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"

# File names (customize if your files have different names)
FILE_NAMES = {
    "B3": "b3_carrteira.xlsx",
    "Kinvo": "kinvo_carteira.xlsx",
    "MyProfit": "myprofit_carteira.xls",
    "XP": "xp_carteira.xlsx",
}

# Deduplication settings
DEDUPLICATION_STRATEGY = "aggregate"  # Options: "aggregate", "prioritize", "latest"

# Source priority (higher number = higher priority)
# Used when deduplication_strategy = "prioritize"
SOURCE_PRIORITY = {
    "MyProfit": 4,  # Most complete data
    "B3": 3,  # Official exchange data
    "XP": 2,  # Brokerage data
    "Kinvo": 1,  # Aggregator platform
}

# Versioning settings
ENABLE_VERSIONING = True
KEEP_SNAPSHOTS = True  # Keep copies of original files

# Visualization settings
VISUALIZATION_DPI = 150  # DPI for PNG exports (higher = better quality, larger file)
CHART_STYLE = "whitegrid"  # seaborn style: whitegrid, darkgrid, white, dark, ticks

# Top N items in reports and charts
TOP_HOLDINGS_COUNT = 20
TOP_GAINS_COUNT = 10
TOP_LOSSES_COUNT = 10

# Currency format
CURRENCY_SYMBOL = "R$"
DECIMAL_SEPARATOR = ","
THOUSANDS_SEPARATOR = "."

# Report settings
CONCENTRATION_THRESHOLD = 0.5  # Warn if top 5 assets > 50% of portfolio
NEGATIVE_RETURN_WARN = True  # Warn if portfolio has negative return

# Performance thresholds for alerts
SIGNIFICANT_CHANGE_THRESHOLD = 0.10  # 10% change is significant
LARGE_POSITION_THRESHOLD = 0.05  # Positions > 5% of portfolio are "large"

# Date format
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"

# Logging
VERBOSE = True  # Show detailed progress information
DEBUG = False  # Show debug information
