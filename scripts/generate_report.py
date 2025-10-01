"""Generate detailed portfolio analysis report."""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def format_currency(value: float) -> str:
    """Format value as Brazilian currency."""
    return f"R$ {value:,.2f}"


def format_percent(value: float) -> str:
    """Format value as percentage."""
    return f"{value:+.2f}%"


def generate_text_report(df: pd.DataFrame, output_file: Path) -> None:
    """Generate comprehensive text report."""
    with open(output_file, "w", encoding="utf-8") as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DETALHADO DE ANÁLISE DE PORTFOLIO\n".center(80))
        f.write("=" * 80 + "\n\n")

        f.write(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total de Ativos: {len(df)}\n")
        f.write("\n")

        # Calculate metrics
        total_value = df["total_value"].sum()
        total_invested = (df["avg_price"] * df["quantity"]).sum()
        total_pl = df["profit_loss"].sum()
        total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0

        # Summary
        f.write("-" * 80 + "\n")
        f.write("RESUMO EXECUTIVO\n")
        f.write("-" * 80 + "\n\n")

        f.write(f"Valor Total Investido: {format_currency(total_invested)}\n")
        f.write(f"Valor Atual do Portfolio: {format_currency(total_value)}\n")
        f.write(f"Lucro/Prejuízo Total: {format_currency(total_pl)}\n")
        f.write(f"Retorno Percentual: {format_percent(total_pl_pct)}\n\n")

        # Distribution by source
        f.write("-" * 80 + "\n")
        f.write("DISTRIBUIÇÃO POR FONTE\n")
        f.write("-" * 80 + "\n\n")

        source_stats = []
        for source in ["B3", "Kinvo", "MyProfit", "XP"]:
            source_assets = df[df["source"].str.contains(source, na=False)]
            if len(source_assets) > 0:
                value = source_assets["total_value"].sum()
                count = len(source_assets)
                pct = (value / total_value * 100) if total_value > 0 else 0
                source_stats.append((source, count, value, pct))

        for source, count, value, pct in sorted(
            source_stats, key=lambda x: x[2], reverse=True
        ):
            f.write(
                f"{source:<15} {count:>4} ativos  {format_currency(value):>18}  ({pct:>5.2f}%)\n"
            )

        f.write("\n")

        # Performance analysis
        f.write("-" * 80 + "\n")
        f.write("ANÁLISE DE PERFORMANCE\n")
        f.write("-" * 80 + "\n\n")

        positive = df[df["profit_loss"] > 0]
        negative = df[df["profit_loss"] < 0]
        neutral = df[df["profit_loss"] == 0]

        f.write(f"Ativos com Lucro: {len(positive)} ({len(positive)/len(df)*100:.1f}%)\n")
        f.write(f"Ativos com Prejuízo: {len(negative)} ({len(negative)/len(df)*100:.1f}%)\n")
        f.write(f"Ativos Neutros: {len(neutral)} ({len(neutral)/len(df)*100:.1f}%)\n\n")

        if len(positive) > 0:
            avg_gain = positive["profit_loss_pct"].mean()
            f.write(f"Ganho Médio (ativos positivos): {format_percent(avg_gain)}\n")

        if len(negative) > 0:
            avg_loss = negative["profit_loss_pct"].mean()
            f.write(f"Perda Média (ativos negativos): {format_percent(avg_loss)}\n")

        f.write("\n")

        # Top performers
        f.write("-" * 80 + "\n")
        f.write("TOP 10 MAIORES GANHOS (%)\n")
        f.write("-" * 80 + "\n\n")

        top_gains = df.nlargest(10, "profit_loss_pct")
        f.write(
            f"{'Ativo':<40} {'Valor':>15} {'Ganho %':>12} {'R$ Ganho':>15}\n"
        )
        f.write("-" * 80 + "\n")

        for _, row in top_gains.iterrows():
            f.write(
                f"{row['ticker']:<40} {format_currency(row['total_value']):>15} "
                f"{format_percent(row['profit_loss_pct']):>12} "
                f"{format_currency(row['profit_loss']):>15}\n"
            )

        f.write("\n")

        # Top losses
        f.write("-" * 80 + "\n")
        f.write("TOP 10 MAIORES PERDAS (%)\n")
        f.write("-" * 80 + "\n\n")

        top_losses = df.nsmallest(10, "profit_loss_pct")
        f.write(
            f"{'Ativo':<40} {'Valor':>15} {'Perda %':>12} {'R$ Perda':>15}\n"
        )
        f.write("-" * 80 + "\n")

        for _, row in top_losses.iterrows():
            f.write(
                f"{row['ticker']:<40} {format_currency(row['total_value']):>15} "
                f"{format_percent(row['profit_loss_pct']):>12} "
                f"{format_currency(row['profit_loss']):>15}\n"
            )

        f.write("\n")

        # Top holdings by value
        f.write("-" * 80 + "\n")
        f.write("TOP 20 MAIORES POSIÇÕES\n")
        f.write("-" * 80 + "\n\n")

        top_value = df.nlargest(20, "total_value")
        f.write(
            f"{'Ativo':<40} {'Valor':>15} {'% Portfolio':>12} {'Fonte':<20}\n"
        )
        f.write("-" * 80 + "\n")

        for _, row in top_value.iterrows():
            pct_portfolio = (row["total_value"] / total_value * 100)
            f.write(
                f"{row['ticker']:<40} {format_currency(row['total_value']):>15} "
                f"{pct_portfolio:>11.2f}% {row['source']:<20}\n"
            )

        f.write("\n")

        # Concentration analysis
        f.write("-" * 80 + "\n")
        f.write("ANÁLISE DE CONCENTRAÇÃO\n")
        f.write("-" * 80 + "\n\n")

        top_5_value = df.nlargest(5, "total_value")["total_value"].sum()
        top_10_value = df.nlargest(10, "total_value")["total_value"].sum()
        top_20_value = df.nlargest(20, "total_value")["total_value"].sum()

        f.write(
            f"Top 5 ativos representam: {format_percent(top_5_value/total_value*100)} do portfolio\n"
        )
        f.write(
            f"Top 10 ativos representam: {format_percent(top_10_value/total_value*100)} do portfolio\n"
        )
        f.write(
            f"Top 20 ativos representam: {format_percent(top_20_value/total_value*100)} do portfolio\n"
        )

        f.write("\n")

        # Recommendations
        f.write("-" * 80 + "\n")
        f.write("RECOMENDAÇÕES\n")
        f.write("-" * 80 + "\n\n")

        if top_5_value / total_value > 0.5:
            f.write(
                "⚠ ATENÇÃO: Alta concentração detectada. Top 5 ativos representam mais de 50% "
                "do portfolio.\n"
            )
            f.write("  Considere diversificar para reduzir risco.\n\n")

        if len(negative) > len(positive):
            f.write(
                "⚠ ATENÇÃO: Mais ativos com prejuízo do que com lucro.\n"
            )
            f.write("  Revise a estratégia de investimento.\n\n")

        if total_pl_pct < 0:
            f.write(
                "⚠ ATENÇÃO: Portfolio com retorno negativo.\n"
            )
            f.write(
                "  Considere rebalanceamento e revisão de ativos com maior perda.\n\n"
            )

        # Footer
        f.write("\n" + "=" * 80 + "\n")
        f.write("FIM DO RELATÓRIO\n".center(80))
        f.write("=" * 80 + "\n")


def main() -> None:
    """Generate comprehensive report."""
    print("📄 Generating Detailed Portfolio Report\n")
    print("=" * 70)

    # Load consolidated portfolio
    csv_file = Path("output/consolidated_portfolio.csv")

    if not csv_file.exists():
        print("❌ Consolidated portfolio not found.")
        print("Run 'python main.py' first to create a consolidation.")
        return

    df = pd.read_csv(csv_file)
    print(f"✓ Loaded {len(df)} assets from {csv_file}")

    # Generate report
    output_file = Path("output/detailed_report.txt")

    try:
        generate_text_report(df, output_file)
        print(f"\n✓ Report generated: {output_file}")

        # Display file size
        size_kb = output_file.stat().st_size / 1024
        print(f"  File size: {size_kb:.1f} KB")

        print("\n" + "=" * 70)
        print("✅ Report generation complete!")
        print(f"\nView report: notepad {output_file}")

    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
