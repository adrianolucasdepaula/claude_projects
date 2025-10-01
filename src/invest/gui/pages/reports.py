"""Reports generation and export page."""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def show() -> None:
    """Display the reports page."""
    st.title("📄 Relatórios e Exportações")
    st.markdown("---")

    st.markdown(
        """
        Gere relatórios detalhados do seu portfolio e exporte em diferentes formatos.
        """
    )

    # Load consolidated portfolio
    output_dir = Path("output/consolidated")
    latest_file = output_dir / "latest.csv"

    if not latest_file.exists():
        st.warning(
            """
            ⚠️ **Nenhum portfolio consolidado encontrado.**

            Por favor, vá para a página **Consolidação** para processar suas planilhas primeiro.
            """
        )
        st.stop()

    try:
        df = pd.read_csv(latest_file)
    except Exception as e:
        st.error(f"❌ Erro ao carregar portfolio: {e}")
        st.stop()

    # Report type selection
    st.subheader("📊 Tipo de Relatório")

    report_type = st.radio(
        "Selecione o tipo de relatório:",
        [
            "📋 Relatório Executivo",
            "📈 Análise de Performance",
            "🔍 Análise Detalhada por Ativo",
            "📊 Distribuição por Categoria",
            "⚠️ Alertas e Recomendações",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Generate selected report
    if report_type == "📋 Relatório Executivo":
        generate_executive_report(df)
    elif report_type == "📈 Análise de Performance":
        generate_performance_report(df)
    elif report_type == "🔍 Análise Detalhada por Ativo":
        generate_detailed_asset_report(df)
    elif report_type == "📊 Distribuição por Categoria":
        generate_distribution_report(df)
    elif report_type == "⚠️ Alertas e Recomendações":
        generate_alerts_report(df)


def generate_executive_report(df: pd.DataFrame) -> None:
    """Generate executive summary report."""
    st.subheader("📋 Relatório Executivo")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_value = df["total_value"].sum()
    num_assets = len(df)
    num_sources = df["source"].nunique()

    with col1:
        st.metric("💰 Valor Total", f"R$ {total_value:,.2f}")
    with col2:
        st.metric("📊 Total de Ativos", num_assets)
    with col3:
        st.metric("🏢 Fontes", num_sources)
    with col4:
        if "profit_loss" in df.columns:
            total_pl = df["profit_loss"].sum()
            st.metric("💹 P&L Total", f"R$ {total_pl:,.2f}")
        else:
            st.metric("💹 P&L Total", "N/A")

    st.markdown("---")

    # Generate report text
    report_text = f"""
# RELATÓRIO EXECUTIVO - PORTFOLIO DE INVESTIMENTOS
**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}

---

## 1. RESUMO GERAL

- **Valor Total do Portfolio:** R$ {total_value:,.2f}
- **Número Total de Ativos:** {num_assets}
- **Número de Fontes:** {num_sources}
- **Fontes:** {', '.join(df['source'].unique())}

## 2. DISTRIBUIÇÃO POR FONTE

"""

    # Distribution by source
    source_dist = df.groupby("source").agg({
        "total_value": "sum",
        "ticker": "count",
    }).reset_index()
    source_dist.columns = ["Fonte", "Valor Total", "Quantidade"]
    source_dist["Percentual"] = (source_dist["Valor Total"] / total_value * 100).round(2)
    source_dist = source_dist.sort_values("Valor Total", ascending=False)

    for _, row in source_dist.iterrows():
        report_text += f"- **{row['Fonte']}:** R$ {row['Valor Total']:,.2f} ({row['Percentual']:.2f}%) - {row['Quantidade']} ativos\n"

    # Top holdings
    report_text += "\n## 3. PRINCIPAIS POSIÇÕES (TOP 10)\n\n"
    top_10 = df.nlargest(10, "total_value")

    for i, row in enumerate(top_10.itertuples(), 1):
        pct = (row.total_value / total_value * 100)
        report_text += f"{i}. **{row.ticker}** - R$ {row.total_value:,.2f} ({pct:.2f}%) - Fonte: {row.source}\n"

    # Performance (if available)
    if "profit_loss" in df.columns:
        total_pl = df["profit_loss"].sum()
        avg_return = df["profit_loss_pct"].mean()

        positive = len(df[df["profit_loss"] > 0])
        negative = len(df[df["profit_loss"] < 0])
        neutral = len(df[df["profit_loss"] == 0])

        report_text += f"""
## 4. PERFORMANCE

- **Lucro/Prejuízo Total:** R$ {total_pl:,.2f}
- **Retorno Médio:** {avg_return:.2f}%
- **Ativos em Lucro:** {positive} ({positive/num_assets*100:.1f}%)
- **Ativos em Prejuízo:** {negative} ({negative/num_assets*100:.1f}%)
- **Ativos Neutros:** {neutral} ({neutral/num_assets*100:.1f}%)
"""

    # Concentration
    top_5_value = df.nlargest(5, "total_value")["total_value"].sum()
    top_5_pct = (top_5_value / total_value * 100)

    report_text += f"""
## 5. CONCENTRAÇÃO

- **Top 5 Ativos:** R$ {top_5_value:,.2f} ({top_5_pct:.2f}% do portfolio)
"""

    if top_5_pct > 50:
        report_text += "- ⚠️ **ATENÇÃO:** Alta concentração detectada (>50% em 5 ativos)\n"
    elif top_5_pct > 30:
        report_text += "- ℹ️ **NOTA:** Concentração moderada (>30% em 5 ativos)\n"
    else:
        report_text += "- ✅ **BOA DIVERSIFICAÇÃO:** Portfolio bem distribuído\n"

    # Display report
    st.markdown(report_text)

    # Download buttons
    st.markdown("---")
    st.subheader("📥 Exportar Relatório")

    col1, col2, col3 = st.columns(3)

    with col1:
        txt_report = report_text.encode("utf-8")
        st.download_button(
            label="📄 Download TXT",
            data=txt_report,
            file_name=f"relatorio_executivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col2:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col3:
        # Create Excel file
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Portfolio")
            source_dist.to_excel(writer, index=False, sheet_name="Distribuição")
            top_10.to_excel(writer, index=False, sheet_name="Top 10")
        buffer.seek(0)

        st.download_button(
            label="📗 Download Excel",
            data=buffer,
            file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


def generate_performance_report(df: pd.DataFrame) -> None:
    """Generate performance analysis report."""
    st.subheader("📈 Análise de Performance")

    if "profit_loss" not in df.columns:
        st.warning("⚠️ Dados de performance não disponíveis neste portfolio")
        return

    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)

    total_pl = df["profit_loss"].sum()
    avg_return = df["profit_loss_pct"].mean()
    best_return = df["profit_loss_pct"].max()
    worst_return = df["profit_loss_pct"].min()

    with col1:
        st.metric("💰 P&L Total", f"R$ {total_pl:,.2f}")
    with col2:
        st.metric("📊 Retorno Médio", f"{avg_return:.2f}%")
    with col3:
        st.metric("🔝 Melhor Retorno", f"{best_return:.2f}%")
    with col4:
        st.metric("📉 Pior Retorno", f"{worst_return:.2f}%")

    # Performance distribution
    st.markdown("### 📊 Distribuição de Performance")

    positive = df[df["profit_loss"] > 0]
    negative = df[df["profit_loss"] < 0]
    neutral = df[df["profit_loss"] == 0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🟢 Em Lucro",
            len(positive),
            delta=f"R$ {positive['profit_loss'].sum():,.2f}",
            delta_color="normal",
        )

    with col2:
        st.metric(
            "🔴 Em Prejuízo",
            len(negative),
            delta=f"R$ {negative['profit_loss'].sum():,.2f}",
            delta_color="inverse",
        )

    with col3:
        st.metric("⚪ Neutro", len(neutral))

    # Top performers
    st.markdown("### 🏆 Melhores Performances")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🟢 Top 10 Ganhos")
        top_gains = positive.nlargest(10, "profit_loss")[
            ["ticker", "profit_loss", "profit_loss_pct", "total_value", "source"]
        ]
        st.dataframe(top_gains, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### 🔴 Top 10 Perdas")
        top_losses = negative.nsmallest(10, "profit_loss")[
            ["ticker", "profit_loss", "profit_loss_pct", "total_value", "source"]
        ]
        st.dataframe(top_losses, use_container_width=True, hide_index=True)

    # Performance by source
    st.markdown("### 📊 Performance por Fonte")

    perf_by_source = df.groupby("source").agg({
        "profit_loss": "sum",
        "profit_loss_pct": "mean",
        "total_value": "sum",
    }).reset_index()
    perf_by_source.columns = ["Fonte", "P&L Total", "Retorno Médio %", "Valor Total"]

    st.dataframe(perf_by_source, use_container_width=True, hide_index=True)


def generate_detailed_asset_report(df: pd.DataFrame) -> None:
    """Generate detailed asset-by-asset report."""
    st.subheader("🔍 Análise Detalhada por Ativo")

    # Search and filter
    col1, col2 = st.columns(2)

    with col1:
        search_term = st.text_input("🔍 Buscar ativo (ticker)", "")

    with col2:
        source_filter = st.multiselect(
            "Filtrar por fonte",
            options=df["source"].unique(),
            default=df["source"].unique(),
        )

    # Apply filters
    filtered_df = df[df["source"].isin(source_filter)]

    if search_term:
        filtered_df = filtered_df[
            filtered_df["ticker"].str.contains(search_term, case=False, na=False)
        ]

    st.info(f"📊 Mostrando {len(filtered_df)} ativos")

    # Detailed table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=600,
    )

    # Export filtered data
    if len(filtered_df) > 0:
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar Dados Filtrados (CSV)",
            data=csv_data,
            file_name=f"ativos_detalhados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )


def generate_distribution_report(df: pd.DataFrame) -> None:
    """Generate distribution analysis report."""
    st.subheader("📊 Distribuição por Categoria")

    # Distribution by source
    st.markdown("### 📈 Distribuição por Fonte")
    source_dist = df.groupby("source").agg({
        "ticker": "count",
        "total_value": "sum",
    }).reset_index()
    source_dist.columns = ["Fonte", "Quantidade", "Valor Total"]
    source_dist["Percentual"] = (source_dist["Valor Total"] / source_dist["Valor Total"].sum() * 100).round(2)
    source_dist = source_dist.sort_values("Valor Total", ascending=False)

    st.dataframe(source_dist, use_container_width=True, hide_index=True)

    # Distribution by asset class (if available)
    if "asset_class" in df.columns:
        st.markdown("### 📊 Distribuição por Classe de Ativo")
        class_dist = df.groupby("asset_class").agg({
            "ticker": "count",
            "total_value": "sum",
        }).reset_index()
        class_dist.columns = ["Classe", "Quantidade", "Valor Total"]
        class_dist["Percentual"] = (class_dist["Valor Total"] / class_dist["Valor Total"].sum() * 100).round(2)
        class_dist = class_dist.sort_values("Valor Total", ascending=False)

        st.dataframe(class_dist, use_container_width=True, hide_index=True)

    # Distribution by category (if available)
    if "category" in df.columns:
        st.markdown("### 🏷️ Distribuição por Categoria")
        category_dist = df.groupby("category").agg({
            "ticker": "count",
            "total_value": "sum",
        }).reset_index()
        category_dist.columns = ["Categoria", "Quantidade", "Valor Total"]
        category_dist["Percentual"] = (category_dist["Valor Total"] / category_dist["Valor Total"].sum() * 100).round(2)
        category_dist = category_dist.sort_values("Valor Total", ascending=False)

        st.dataframe(category_dist, use_container_width=True, hide_index=True)


def generate_alerts_report(df: pd.DataFrame) -> None:
    """Generate alerts and recommendations report."""
    st.subheader("⚠️ Alertas e Recomendações")

    alerts = []

    # Concentration alerts
    total_value = df["total_value"].sum()
    top_5_value = df.nlargest(5, "total_value")["total_value"].sum()
    top_5_pct = (top_5_value / total_value * 100)

    if top_5_pct > 50:
        alerts.append({
            "tipo": "⚠️ ALERTA",
            "categoria": "Concentração",
            "mensagem": f"Alta concentração: Top 5 ativos representam {top_5_pct:.2f}% do portfolio",
            "recomendacao": "Considere diversificar reduzindo exposição aos ativos mais concentrados",
        })
    elif top_5_pct > 30:
        alerts.append({
            "tipo": "ℹ️ INFO",
            "categoria": "Concentração",
            "mensagem": f"Concentração moderada: Top 5 ativos representam {top_5_pct:.2f}% do portfolio",
            "recomendacao": "Monitore a concentração para evitar exposição excessiva",
        })

    # Performance alerts (if available)
    if "profit_loss_pct" in df.columns:
        # Large losses alert
        large_losses = df[df["profit_loss_pct"] < -20]
        if len(large_losses) > 0:
            alerts.append({
                "tipo": "⚠️ ALERTA",
                "categoria": "Performance",
                "mensagem": f"{len(large_losses)} ativos com perdas superiores a 20%",
                "recomendacao": "Revisar posições com grandes perdas para decisão de manutenção ou realização",
            })

        # Average return alert
        avg_return = df["profit_loss_pct"].mean()
        if avg_return < 0:
            alerts.append({
                "tipo": "⚠️ ALERTA",
                "categoria": "Performance",
                "mensagem": f"Retorno médio negativo: {avg_return:.2f}%",
                "recomendacao": "Portfolio com performance negativa - revisar estratégia de investimento",
            })

    # Asset quantity alerts
    if len(df) > 100:
        alerts.append({
            "tipo": "ℹ️ INFO",
            "categoria": "Diversificação",
            "mensagem": f"Portfolio com {len(df)} ativos - muito diversificado",
            "recomendacao": "Considere consolidar em ativos de maior convicção para facilitar gestão",
        })
    elif len(df) < 10:
        alerts.append({
            "tipo": "ℹ️ INFO",
            "categoria": "Diversificação",
            "mensagem": f"Portfolio com apenas {len(df)} ativos - pouco diversificado",
            "recomendacao": "Considere aumentar diversificação para reduzir risco específico",
        })

    # Small positions alert
    small_positions = df[df["total_value"] < (total_value * 0.01)]  # < 1% of portfolio
    if len(small_positions) > 10:
        alerts.append({
            "tipo": "ℹ️ INFO",
            "categoria": "Posições Pequenas",
            "mensagem": f"{len(small_positions)} posições representam menos de 1% do portfolio cada",
            "recomendacao": "Considere consolidar ou eliminar posições muito pequenas",
        })

    # Display alerts
    if not alerts:
        st.success("✅ Nenhum alerta detectado. Portfolio dentro dos parâmetros normais.")
    else:
        for alert in alerts:
            if alert["tipo"] == "⚠️ ALERTA":
                st.warning(f"**{alert['categoria']}**: {alert['mensagem']}\n\n💡 {alert['recomendacao']}")
            else:
                st.info(f"**{alert['categoria']}**: {alert['mensagem']}\n\n💡 {alert['recomendacao']}")

    # Summary table
    if alerts:
        st.markdown("---")
        st.markdown("### 📋 Resumo de Alertas")
        alerts_df = pd.DataFrame(alerts)
        st.dataframe(alerts_df, use_container_width=True, hide_index=True)
