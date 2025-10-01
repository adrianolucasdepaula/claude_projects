"""Generate portfolio visualizations."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams["font.size"] = 10


def create_top_holdings_chart(df: pd.DataFrame, output_dir: Path) -> Path:
    """Create horizontal bar chart of top holdings."""
    top_20 = df.nlargest(20, "total_value")

    fig, ax = plt.subplots(figsize=(12, 10))

    colors = ["#2ecc71" if x > 0 else "#e74c3c" for x in top_20["profit_loss_pct"]]

    ax.barh(top_20["ticker"], top_20["total_value"], color=colors, alpha=0.7)
    ax.set_xlabel("Valor Total (R$)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Ativo", fontsize=12, fontweight="bold")
    ax.set_title(
        "Top 20 Holdings por Valor Total", fontsize=14, fontweight="bold", pad=20
    )

    # Format x-axis as currency
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"R$ {x/1000:.0f}K"))

    # Add value labels
    for i, (idx, row) in enumerate(top_20.iterrows()):
        value = row["total_value"]
        pct = row["profit_loss_pct"]
        label = f" R$ {value:,.0f} ({pct:+.1f}%)"
        ax.text(value, i, label, va="center", ha="left", fontsize=8)

    plt.tight_layout()

    output_file = output_dir / "top_holdings.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()

    return output_file


def create_source_distribution(df: pd.DataFrame, output_dir: Path) -> Path:
    """Create pie chart of portfolio distribution by source."""
    # Expand sources (some assets have multiple sources)
    source_values = []
    for _, row in df.iterrows():
        sources = row["source"].split(", ")
        value_per_source = row["total_value"] / len(sources)
        for source in sources:
            source_values.append({"source": source, "value": value_per_source})

    source_df = pd.DataFrame(source_values)
    source_summary = source_df.groupby("source")["value"].sum().sort_values(
        ascending=False
    )

    fig, ax = plt.subplots(figsize=(10, 8))

    colors = sns.color_palette("husl", len(source_summary))
    wedges, texts, autotexts = ax.pie(
        source_summary,
        labels=source_summary.index,
        autopct=lambda pct: f"{pct:.1f}%\nR$ {pct/100 * source_summary.sum()/1000:.0f}K",
        startangle=90,
        colors=colors,
        textprops={"fontsize": 10},
    )

    ax.set_title(
        "Distribuição do Portfolio por Fonte", fontsize=14, fontweight="bold", pad=20
    )

    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    plt.tight_layout()

    output_file = output_dir / "source_distribution.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()

    return output_file


def create_profit_loss_distribution(df: pd.DataFrame, output_dir: Path) -> Path:
    """Create histogram of profit/loss distribution."""
    # Filter out extreme outliers for better visualization
    q1 = df["profit_loss_pct"].quantile(0.05)
    q99 = df["profit_loss_pct"].quantile(0.95)
    filtered_df = df[
        (df["profit_loss_pct"] >= q1) & (df["profit_loss_pct"] <= q99)
    ].copy()

    fig, ax = plt.subplots(figsize=(12, 6))

    # Create histogram
    n, bins, patches = ax.hist(
        filtered_df["profit_loss_pct"], bins=30, edgecolor="black", alpha=0.7
    )

    # Color bars by profit/loss
    for i, patch in enumerate(patches):
        if bins[i] < 0:
            patch.set_facecolor("#e74c3c")
        else:
            patch.set_facecolor("#2ecc71")

    ax.axvline(x=0, color="black", linestyle="--", linewidth=2, label="Break-even")
    ax.set_xlabel("Lucro/Prejuízo (%)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Número de Ativos", fontsize=12, fontweight="bold")
    ax.set_title(
        "Distribuição de Lucro/Prejuízo dos Ativos",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.legend()

    # Add statistics text
    stats_text = (
        f"Média: {filtered_df['profit_loss_pct'].mean():.2f}%\n"
        f"Mediana: {filtered_df['profit_loss_pct'].median():.2f}%\n"
        f"Positivos: {(filtered_df['profit_loss_pct'] > 0).sum()} ativos\n"
        f"Negativos: {(filtered_df['profit_loss_pct'] < 0).sum()} ativos"
    )
    ax.text(
        0.02,
        0.98,
        stats_text,
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        fontsize=10,
    )

    plt.tight_layout()

    output_file = output_dir / "profit_loss_distribution.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()

    return output_file


def create_summary_dashboard(df: pd.DataFrame, output_dir: Path) -> Path:
    """Create a summary dashboard with key metrics."""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # Calculate metrics
    total_value = df["total_value"].sum()
    total_invested = (df["avg_price"] * df["quantity"]).sum()
    total_pl = df["profit_loss"].sum()
    total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0

    positive_assets = (df["profit_loss"] > 0).sum()
    negative_assets = (df["profit_loss"] < 0).sum()

    # Title
    fig.suptitle(
        "Dashboard de Investimentos", fontsize=20, fontweight="bold", y=0.98
    )

    # Metric cards
    metrics = [
        ("Valor Total", f"R$ {total_value:,.2f}", "#3498db"),
        ("Investido", f"R$ {total_invested:,.2f}", "#95a5a6"),
        ("Lucro/Prejuízo", f"R$ {total_pl:,.2f}", "#2ecc71" if total_pl > 0 else "#e74c3c"),
        ("Retorno %", f"{total_pl_pct:+.2f}%", "#2ecc71" if total_pl_pct > 0 else "#e74c3c"),
        ("Total Ativos", str(len(df)), "#9b59b6"),
        ("Lucro", f"{positive_assets} ativos", "#2ecc71"),
    ]

    for i, (label, value, color) in enumerate(metrics[:6]):
        row = i // 3
        col = i % 3
        ax = fig.add_subplot(gs[row, col])
        ax.text(
            0.5,
            0.6,
            value,
            ha="center",
            va="center",
            fontsize=24,
            fontweight="bold",
            color=color,
        )
        ax.text(
            0.5,
            0.3,
            label,
            ha="center",
            va="center",
            fontsize=14,
            color="gray",
        )
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # Add border
        rect = plt.Rectangle(
            (0.05, 0.1), 0.9, 0.8, fill=False, edgecolor=color, linewidth=2
        )
        ax.add_patch(rect)

    # Top 10 chart
    ax_top = fig.add_subplot(gs[2, :2])
    top_10 = df.nlargest(10, "total_value")
    colors_top = ["#2ecc71" if x > 0 else "#e74c3c" for x in top_10["profit_loss_pct"]]
    ax_top.barh(top_10["ticker"], top_10["total_value"], color=colors_top, alpha=0.7)
    ax_top.set_xlabel("Valor (R$)")
    ax_top.set_title("Top 10 Holdings", fontweight="bold")
    ax_top.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f"R$ {x/1000:.0f}K")
    )

    # P/L distribution
    ax_pl = fig.add_subplot(gs[2, 2])
    pl_data = [positive_assets, negative_assets]
    ax_pl.pie(
        pl_data,
        labels=["Lucro", "Prejuízo"],
        autopct="%1.1f%%",
        colors=["#2ecc71", "#e74c3c"],
        startangle=90,
    )
    ax_pl.set_title("Distribuição L/P", fontweight="bold")

    output_file = output_dir / "dashboard.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()

    return output_file


def main() -> None:
    """Generate all visualizations."""
    print("📊 Generating Portfolio Visualizations\n")
    print("=" * 70)

    # Load consolidated portfolio
    csv_file = Path("output/consolidated_portfolio.csv")

    if not csv_file.exists():
        print("❌ Consolidated portfolio not found.")
        print("Run 'python main.py' first to create a consolidation.")
        return

    df = pd.read_csv(csv_file)
    print(f"✓ Loaded {len(df)} assets from {csv_file}")

    # Create output directory
    output_dir = Path("output/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate charts
    print("\nGenerating visualizations...")

    try:
        file1 = create_summary_dashboard(df, output_dir)
        print(f"  ✓ Dashboard: {file1}")

        file2 = create_top_holdings_chart(df, output_dir)
        print(f"  ✓ Top Holdings: {file2}")

        file3 = create_source_distribution(df, output_dir)
        print(f"  ✓ Source Distribution: {file3}")

        file4 = create_profit_loss_distribution(df, output_dir)
        print(f"  ✓ P/L Distribution: {file4}")

        print("\n" + "=" * 70)
        print(f"✅ All visualizations saved to: {output_dir}")
        print("\nGenerated files:")
        for file in sorted(output_dir.glob("*.png")):
            print(f"  - {file.name}")

    except Exception as e:
        print(f"\n❌ Error generating visualizations: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
