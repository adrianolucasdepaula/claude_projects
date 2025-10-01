"""Version comparison page."""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def show() -> None:
    """Display the version comparison page."""
    st.title("📊 Comparação de Versões")
    st.markdown("---")

    st.markdown(
        """
        Compare diferentes versões consolidadas do seu portfolio para identificar mudanças,
        novos ativos, ativos removidos e variações de valor.
        """
    )

    # Find available versions
    consolidated_dir = Path("output/consolidated")
    if not consolidated_dir.exists():
        st.warning("⚠️ Nenhuma versão consolidada encontrada. Faça uma consolidação primeiro.")
        st.stop()

    # Get all consolidated files
    csv_files = sorted(consolidated_dir.glob("portfolio_*.csv"), reverse=True)

    if len(csv_files) < 2:
        st.info(
            f"""
            ℹ️ **Apenas {len(csv_files)} versão encontrada.**

            Faça pelo menos 2 consolidações para poder comparar versões.
            """
        )
        if len(csv_files) == 1:
            st.write(f"Versão disponível: `{csv_files[0].name}`")
        st.stop()

    # Version selection
    st.subheader("📅 Selecionar Versões para Comparar")

    col1, col2 = st.columns(2)

    version_names = [f.stem.replace("portfolio_", "") for f in csv_files]

    with col1:
        version1 = st.selectbox(
            "Versão 1 (Anterior)",
            options=version_names,
            index=min(1, len(version_names) - 1),
            help="Selecione a versão mais antiga",
        )

    with col2:
        version2 = st.selectbox(
            "Versão 2 (Atual)",
            options=version_names,
            index=0,
            help="Selecione a versão mais recente",
        )

    if version1 == version2:
        st.warning("⚠️ Por favor, selecione duas versões diferentes para comparar")
        st.stop()

    # Load versions
    try:
        df1 = pd.read_csv(consolidated_dir / f"portfolio_{version1}.csv")
        df2 = pd.read_csv(consolidated_dir / f"portfolio_{version2}.csv")
    except Exception as e:
        st.error(f"❌ Erro ao carregar versões: {e}")
        st.stop()

    # Perform comparison
    if st.button("🔍 Comparar Versões", type="primary", use_container_width=True):
        compare_versions(df1, df2, version1, version2)


def compare_versions(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    version1: str,
    version2: str,
) -> None:
    """
    Compare two portfolio versions.

    Args:
        df1: First (older) version DataFrame
        df2: Second (newer) version DataFrame
        version1: Name of first version
        version2: Name of second version
    """
    st.markdown("---")
    st.subheader("📊 Resultados da Comparação")

    # Overall metrics comparison
    col1, col2, col3, col4 = st.columns(4)

    total_value_1 = df1["total_value"].sum()
    total_value_2 = df2["total_value"].sum()
    value_change = total_value_2 - total_value_1
    value_change_pct = (value_change / total_value_1) * 100 if total_value_1 > 0 else 0

    with col1:
        st.metric(
            "Valor Total",
            f"R$ {total_value_2:,.2f}",
            delta=f"R$ {value_change:,.2f}",
            delta_color="normal" if value_change >= 0 else "inverse",
        )

    with col2:
        assets_1 = len(df1)
        assets_2 = len(df2)
        st.metric(
            "Total de Ativos",
            assets_2,
            delta=assets_2 - assets_1,
        )

    with col3:
        unique_1 = df1["ticker"].nunique()
        unique_2 = df2["ticker"].nunique()
        st.metric(
            "Ativos Únicos",
            unique_2,
            delta=unique_2 - unique_1,
        )

    with col4:
        sources_1 = df1["source"].nunique()
        sources_2 = df2["source"].nunique()
        st.metric(
            "Fontes",
            sources_2,
            delta=sources_2 - sources_1,
        )

    # Value change summary
    if value_change != 0:
        change_type = "aumento" if value_change > 0 else "redução"
        st.info(
            f"💰 Portfolio teve {change_type} de **R$ {abs(value_change):,.2f}** "
            f"({abs(value_change_pct):.2f}%) entre as versões"
        )

    st.markdown("---")

    # New and removed assets
    tickers_1 = set(df1["ticker"])
    tickers_2 = set(df2["ticker"])

    new_assets = tickers_2 - tickers_1
    removed_assets = tickers_1 - tickers_2
    common_assets = tickers_1 & tickers_2

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🆕 Novos Ativos", len(new_assets))
    with col2:
        st.metric("❌ Ativos Removidos", len(removed_assets))
    with col3:
        st.metric("🔄 Ativos Mantidos", len(common_assets))

    # Details tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🆕 Novos Ativos",
        "❌ Ativos Removidos",
        "📈 Mudanças de Valor",
        "📊 Comparação Visual",
    ])

    with tab1:
        show_new_assets(df2, new_assets)

    with tab2:
        show_removed_assets(df1, removed_assets)

    with tab3:
        show_value_changes(df1, df2, common_assets)

    with tab4:
        show_visual_comparison(df1, df2, version1, version2)


def show_new_assets(df: pd.DataFrame, new_assets: set) -> None:
    """Show new assets added in the newer version."""
    if not new_assets:
        st.info("✅ Nenhum ativo novo adicionado")
        return

    st.markdown(f"### 🆕 {len(new_assets)} Novos Ativos")

    new_df = df[df["ticker"].isin(new_assets)].copy()
    new_df = new_df.sort_values("total_value", ascending=False)

    # Summary
    total_new_value = new_df["total_value"].sum()
    st.write(f"**Valor total dos novos ativos:** R$ {total_new_value:,.2f}")

    # Table
    display_cols = ["ticker", "quantity", "avg_price", "current_price", "total_value", "source"]
    st.dataframe(
        new_df[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    # Chart
    if len(new_df) > 0:
        fig = px.bar(
            new_df.head(10),
            x="total_value",
            y="ticker",
            orientation="h",
            title="Top 10 Novos Ativos por Valor",
            color="source",
            text="total_value",
        )
        fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)


def show_removed_assets(df: pd.DataFrame, removed_assets: set) -> None:
    """Show assets removed in the newer version."""
    if not removed_assets:
        st.info("✅ Nenhum ativo removido")
        return

    st.markdown(f"### ❌ {len(removed_assets)} Ativos Removidos")

    removed_df = df[df["ticker"].isin(removed_assets)].copy()
    removed_df = removed_df.sort_values("total_value", ascending=False)

    # Summary
    total_removed_value = removed_df["total_value"].sum()
    st.write(f"**Valor total dos ativos removidos:** R$ {total_removed_value:,.2f}")

    # Table
    display_cols = ["ticker", "quantity", "avg_price", "current_price", "total_value", "source"]
    st.dataframe(
        removed_df[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    # Chart
    if len(removed_df) > 0:
        fig = px.bar(
            removed_df.head(10),
            x="total_value",
            y="ticker",
            orientation="h",
            title="Top 10 Ativos Removidos por Valor",
            color="source",
            text="total_value",
        )
        fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)


def show_value_changes(df1: pd.DataFrame, df2: pd.DataFrame, common_assets: set) -> None:
    """Show value changes for common assets."""
    if not common_assets:
        st.info("Nenhum ativo em comum entre as versões")
        return

    st.markdown("### 📈 Mudanças de Valor em Ativos Comuns")

    # Compare values
    changes = []
    for ticker in common_assets:
        val1 = df1[df1["ticker"] == ticker]["total_value"].sum()
        val2 = df2[df2["ticker"] == ticker]["total_value"].sum()
        change = val2 - val1
        change_pct = (change / val1 * 100) if val1 > 0 else 0

        changes.append({
            "ticker": ticker,
            "valor_anterior": val1,
            "valor_atual": val2,
            "mudanca": change,
            "mudanca_pct": change_pct,
        })

    changes_df = pd.DataFrame(changes)
    changes_df = changes_df.sort_values("mudanca", ascending=False)

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        show_filter = st.selectbox(
            "Filtrar",
            ["Todos", "Apenas Aumentos", "Apenas Reduções", "Mudanças Significativas (>10%)"],
        )

    if show_filter == "Apenas Aumentos":
        changes_df = changes_df[changes_df["mudanca"] > 0]
    elif show_filter == "Apenas Reduções":
        changes_df = changes_df[changes_df["mudanca"] < 0]
    elif show_filter == "Mudanças Significativas (>10%)":
        changes_df = changes_df[abs(changes_df["mudanca_pct"]) > 10]

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        increases = len(changes_df[changes_df["mudanca"] > 0])
        st.metric("↗️ Aumentos", increases)
    with col2:
        decreases = len(changes_df[changes_df["mudanca"] < 0])
        st.metric("↘️ Reduções", decreases)
    with col3:
        unchanged = len(changes_df[changes_df["mudanca"] == 0])
        st.metric("➡️ Sem mudança", unchanged)

    # Data table
    st.dataframe(
        changes_df.head(50),
        use_container_width=True,
        hide_index=True,
        column_config={
            "valor_anterior": st.column_config.NumberColumn("Valor Anterior", format="R$ %.2f"),
            "valor_atual": st.column_config.NumberColumn("Valor Atual", format="R$ %.2f"),
            "mudanca": st.column_config.NumberColumn("Mudança", format="R$ %.2f"),
            "mudanca_pct": st.column_config.NumberColumn("Mudança %", format="%.2f%%"),
        },
    )

    # Top changes chart
    col1, col2 = st.columns(2)

    with col1:
        top_increases = changes_df[changes_df["mudanca"] > 0].head(10)
        if len(top_increases) > 0:
            fig = px.bar(
                top_increases,
                x="mudanca",
                y="ticker",
                orientation="h",
                title="Top 10 Maiores Aumentos",
                text="mudanca",
                color="mudanca_pct",
                color_continuous_scale="Greens",
            )
            fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_decreases = changes_df[changes_df["mudanca"] < 0].nsmallest(10, "mudanca")
        if len(top_decreases) > 0:
            fig = px.bar(
                top_decreases,
                x="mudanca",
                y="ticker",
                orientation="h",
                title="Top 10 Maiores Reduções",
                text="mudanca",
                color="mudanca_pct",
                color_continuous_scale="Reds",
            )
            fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
            fig.update_layout(yaxis={"categoryorder": "total descending"})
            st.plotly_chart(fig, use_container_width=True)


def show_visual_comparison(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    version1: str,
    version2: str,
) -> None:
    """Show visual comparison charts."""
    st.markdown("### 📊 Comparação Visual")

    # Total value by source
    source_comp_1 = df1.groupby("source")["total_value"].sum().reset_index()
    source_comp_1["version"] = version1
    source_comp_2 = df2.groupby("source")["total_value"].sum().reset_index()
    source_comp_2["version"] = version2

    source_comp = pd.concat([source_comp_1, source_comp_2], ignore_index=True)

    fig = px.bar(
        source_comp,
        x="source",
        y="total_value",
        color="version",
        barmode="group",
        title="Comparação de Valor por Fonte",
        text="total_value",
    )
    fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # Asset count comparison
    asset_count_1 = df1.groupby("source").size().reset_index(name="count")
    asset_count_1["version"] = version1
    asset_count_2 = df2.groupby("source").size().reset_index(name="count")
    asset_count_2["version"] = version2

    asset_count = pd.concat([asset_count_1, asset_count_2], ignore_index=True)

    fig = px.bar(
        asset_count,
        x="source",
        y="count",
        color="version",
        barmode="group",
        title="Comparação de Quantidade de Ativos por Fonte",
        text="count",
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
