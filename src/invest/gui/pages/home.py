"""Home/Dashboard page for the portfolio analysis application."""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def show() -> None:
    """Display the home/dashboard page."""
    st.title("📊 Portfolio Analysis Dashboard")
    st.markdown("---")

    # Check for latest consolidated portfolio
    output_dir = Path("output/consolidated")
    latest_file = output_dir / "latest.csv"

    if not latest_file.exists():
        st.warning(
            """
            ⚠️ **Nenhum portfolio consolidado encontrado.**

            Por favor, vá para a página **Consolidação** para processar suas planilhas.
            """
        )
        st.stop()

    # Load consolidated portfolio
    try:
        df = pd.read_csv(latest_file)
        st.success(f"✅ Portfolio carregado com sucesso! ({len(df)} ativos)")
    except Exception as e:
        st.error(f"❌ Erro ao carregar portfolio: {e}")
        st.stop()

    # Load metadata if available
    meta_file = output_dir / "latest_meta.json"
    if not meta_file.exists():
        # Try to find the most recent meta file
        meta_files = sorted(output_dir.glob("portfolio_*_meta.json"), reverse=True)
        if meta_files:
            meta_file = meta_files[0]

    metadata = {}
    if meta_file.exists():
        import json

        with open(meta_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    # Display key metrics in cards
    col1, col2, col3, col4 = st.columns(4)

    total_value = df["total_value"].sum()
    unique_tickers = df["ticker"].nunique()
    avg_profit = df["profit_loss_pct"].mean() if "profit_loss_pct" in df.columns else 0
    num_sources = df["source"].nunique()

    with col1:
        st.metric(
            label="💰 Valor Total",
            value=f"R$ {total_value:,.2f}",
            delta=None,
        )

    with col2:
        st.metric(
            label="📊 Ativos Únicos",
            value=unique_tickers,
            delta=None,
        )

    with col3:
        if "profit_loss_pct" in df.columns:
            st.metric(
                label="📈 Retorno Médio",
                value=f"{avg_profit:.2f}%",
                delta=None,
                delta_color="normal" if avg_profit >= 0 else "inverse",
            )
        else:
            st.metric(label="📈 Retorno Médio", value="N/A")

    with col4:
        st.metric(
            label="🔗 Fontes",
            value=num_sources,
            delta=None,
        )

    st.markdown("---")

    # Distribution charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Distribuição por Fonte")
        source_dist = df.groupby("source")["total_value"].sum().reset_index()
        source_dist = source_dist.sort_values("total_value", ascending=False)

        fig = px.pie(
            source_dist,
            values="total_value",
            names="source",
            title="Valor por Fonte",
            hole=0.4,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🏆 Top 10 Holdings")
        top_holdings = df.nlargest(10, "total_value")[["ticker", "total_value", "source"]]

        fig = px.bar(
            top_holdings,
            x="total_value",
            y="ticker",
            orientation="h",
            title="Maiores Posições",
            color="source",
            text="total_value",
        )
        fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Performance analysis (if profit_loss data available)
    if "profit_loss" in df.columns and "profit_loss_pct" in df.columns:
        st.subheader("💹 Análise de Performance")

        col1, col2 = st.columns(2)

        with col1:
            # Profit/Loss distribution
            df["performance_category"] = df["profit_loss_pct"].apply(
                lambda x: "Lucro" if x > 0 else ("Prejuízo" if x < 0 else "Neutro")
            )
            perf_dist = df.groupby("performance_category")["total_value"].sum().reset_index()

            fig = px.bar(
                perf_dist,
                x="performance_category",
                y="total_value",
                title="Distribuição Lucro/Prejuízo",
                color="performance_category",
                color_discrete_map={"Lucro": "green", "Prejuízo": "red", "Neutro": "gray"},
                text="total_value",
            )
            fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Top gains and losses
            tab1, tab2 = st.tabs(["🟢 Maiores Ganhos", "🔴 Maiores Perdas"])

            with tab1:
                top_gains = (
                    df[df["profit_loss"] > 0]
                    .nlargest(5, "profit_loss")[["ticker", "profit_loss", "profit_loss_pct"]]
                    .reset_index(drop=True)
                )
                if len(top_gains) > 0:
                    top_gains.columns = ["Ticker", "Lucro (R$)", "Retorno (%)"]
                    st.dataframe(top_gains, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum ativo com ganhos")

            with tab2:
                top_losses = (
                    df[df["profit_loss"] < 0]
                    .nsmallest(5, "profit_loss")[["ticker", "profit_loss", "profit_loss_pct"]]
                    .reset_index(drop=True)
                )
                if len(top_losses) > 0:
                    top_losses.columns = ["Ticker", "Prejuízo (R$)", "Retorno (%)"]
                    st.dataframe(top_losses, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum ativo com perdas")

    st.markdown("---")

    # Portfolio details table
    st.subheader("📋 Detalhes do Portfolio")

    # Format display columns
    display_df = df.copy()

    # Select and rename columns for display
    display_cols = ["ticker", "quantity", "avg_price", "current_price", "total_value", "source"]
    if "profit_loss" in df.columns:
        display_cols.insert(5, "profit_loss")
    if "profit_loss_pct" in df.columns:
        display_cols.insert(6, "profit_loss_pct")

    display_df = display_df[display_cols]
    display_df.columns = [
        col.replace("_", " ").title() for col in display_df.columns
    ]

    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        selected_source = st.multiselect(
            "Filtrar por Fonte",
            options=df["source"].unique(),
            default=df["source"].unique(),
        )
    with col2:
        min_value = st.slider(
            "Valor Mínimo (R$)",
            min_value=float(df["total_value"].min()),
            max_value=float(df["total_value"].max()),
            value=float(df["total_value"].min()),
        )

    # Apply filters
    filtered_df = df[
        (df["source"].isin(selected_source)) & (df["total_value"] >= min_value)
    ]

    # Prepare display
    filtered_display = filtered_df[display_cols].copy()
    filtered_display.columns = [col.replace("_", " ").title() for col in display_cols]

    st.dataframe(
        filtered_display,
        use_container_width=True,
        hide_index=True,
        height=400,
    )

    # Metadata info
    if metadata:
        with st.expander("ℹ️ Informações da Consolidação"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Data:** {metadata.get('consolidation_date', 'N/A')}")
                st.write(f"**Total de Ativos:** {metadata.get('total_assets', len(df))}")
                st.write(f"**Ativos Únicos:** {metadata.get('unique_assets', df['ticker'].nunique())}")
            with col2:
                st.write(f"**Duplicatas Detectadas:** {metadata.get('duplicates_found', 'N/A')}")
                st.write(f"**Estratégia:** {metadata.get('deduplication_strategy', 'N/A')}")
                st.write(f"**Valor Total:** R$ {metadata.get('total_value', total_value):,.2f}")
