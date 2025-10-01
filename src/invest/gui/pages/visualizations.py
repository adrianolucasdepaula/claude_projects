"""Interactive visualizations page."""

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
    """Display the visualizations page."""
    st.title("📈 Visualizações Interativas")
    st.markdown("---")

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

    # Filters sidebar
    st.sidebar.subheader("🔍 Filtros")

    # Source filter
    sources = st.sidebar.multiselect(
        "Fontes",
        options=df["source"].unique(),
        default=df["source"].unique(),
    )

    # Value range filter
    min_val, max_val = st.sidebar.slider(
        "Faixa de Valor (R$)",
        min_value=float(df["total_value"].min()),
        max_value=float(df["total_value"].max()),
        value=(float(df["total_value"].min()), float(df["total_value"].max())),
        format="R$ %.2f",
    )

    # Apply filters
    filtered_df = df[
        (df["source"].isin(sources))
        & (df["total_value"] >= min_val)
        & (df["total_value"] <= max_val)
    ]

    st.info(f"📊 Exibindo {len(filtered_df)} de {len(df)} ativos")

    # Visualization tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Distribuição",
        "🏆 Top Holdings",
        "💹 Performance",
        "🗺️ Treemap",
        "📈 Análise de Concentração",
    ])

    with tab1:
        show_distribution_charts(filtered_df)

    with tab2:
        show_top_holdings(filtered_df)

    with tab3:
        show_performance_analysis(filtered_df)

    with tab4:
        show_treemap(filtered_df)

    with tab5:
        show_concentration_analysis(filtered_df)


def show_distribution_charts(df: pd.DataFrame) -> None:
    """Show distribution charts."""
    st.subheader("📊 Distribuição do Portfolio")

    col1, col2 = st.columns(2)

    with col1:
        # Distribution by source
        source_dist = df.groupby("source")["total_value"].sum().reset_index()
        source_dist = source_dist.sort_values("total_value", ascending=False)

        fig = px.pie(
            source_dist,
            values="total_value",
            names="source",
            title="Distribuição por Fonte",
            hole=0.4,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Distribution by asset class (if available)
        if "asset_class" in df.columns:
            class_dist = df.groupby("asset_class")["total_value"].sum().reset_index()
            class_dist = class_dist.sort_values("total_value", ascending=False)

            fig = px.pie(
                class_dist,
                values="total_value",
                names="asset_class",
                title="Distribuição por Classe de Ativo",
                hole=0.4,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados de classe de ativo não disponíveis")

    # Bar chart: value by source
    st.subheader("Valor por Fonte")
    source_bar = df.groupby("source")["total_value"].sum().reset_index()
    source_bar = source_bar.sort_values("total_value", ascending=True)

    fig = px.bar(
        source_bar,
        x="total_value",
        y="source",
        orientation="h",
        title="Valor Total por Fonte",
        text="total_value",
        color="source",
    )
    fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def show_top_holdings(df: pd.DataFrame) -> None:
    """Show top holdings analysis."""
    st.subheader("🏆 Principais Posições")

    # Number of top holdings to show
    n_top = st.slider("Número de ativos", min_value=5, max_value=50, value=20, step=5)

    top_n = df.nlargest(n_top, "total_value")

    # Horizontal bar chart
    fig = px.bar(
        top_n,
        x="total_value",
        y="ticker",
        orientation="h",
        title=f"Top {n_top} Holdings por Valor",
        color="source",
        text="total_value",
        hover_data=["quantity", "avg_price", "current_price"],
    )
    fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=max(400, n_top * 20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Data table
    with st.expander("📋 Ver Detalhes"):
        display_cols = ["ticker", "quantity", "avg_price", "current_price", "total_value", "source"]
        if "profit_loss" in top_n.columns:
            display_cols.insert(-1, "profit_loss")
        if "profit_loss_pct" in top_n.columns:
            display_cols.insert(-1, "profit_loss_pct")

        st.dataframe(
            top_n[display_cols],
            use_container_width=True,
            hide_index=True,
        )


def show_performance_analysis(df: pd.DataFrame) -> None:
    """Show performance analysis charts."""
    st.subheader("💹 Análise de Performance")

    if "profit_loss" not in df.columns or "profit_loss_pct" not in df.columns:
        st.warning("⚠️ Dados de performance não disponíveis neste portfolio")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Performance category distribution
        df["performance_category"] = df["profit_loss_pct"].apply(
            lambda x: "Lucro" if x > 0 else ("Prejuízo" if x < 0 else "Neutro")
        )
        perf_count = df.groupby("performance_category").size().reset_index(name="count")
        perf_value = df.groupby("performance_category")["total_value"].sum().reset_index()

        fig = px.pie(
            perf_count,
            values="count",
            names="performance_category",
            title="Distribuição por Performance (Quantidade)",
            color="performance_category",
            color_discrete_map={"Lucro": "green", "Prejuízo": "red", "Neutro": "gray"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            perf_value,
            values="total_value",
            names="performance_category",
            title="Distribuição por Performance (Valor)",
            color="performance_category",
            color_discrete_map={"Lucro": "green", "Prejuízo": "red", "Neutro": "gray"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # Top gains and losses
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🟢 Top 10 Ganhos")
        top_gains = df[df["profit_loss"] > 0].nlargest(10, "profit_loss")

        fig = px.bar(
            top_gains,
            x="profit_loss",
            y="ticker",
            orientation="h",
            title="Maiores Ganhos Absolutos",
            color="profit_loss_pct",
            color_continuous_scale="Greens",
            text="profit_loss",
        )
        fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🔴 Top 10 Perdas")
        top_losses = df[df["profit_loss"] < 0].nsmallest(10, "profit_loss")

        fig = px.bar(
            top_losses,
            x="profit_loss",
            y="ticker",
            orientation="h",
            title="Maiores Perdas Absolutas",
            color="profit_loss_pct",
            color_continuous_scale="Reds",
            text="profit_loss",
        )
        fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis={"categoryorder": "total descending"})
        st.plotly_chart(fig, use_container_width=True)

    # Scatter plot: return vs value
    st.markdown("### 📊 Retorno vs Valor Investido")
    fig = px.scatter(
        df[df["profit_loss_pct"].notna()],
        x="total_value",
        y="profit_loss_pct",
        color="source",
        size="total_value",
        hover_data=["ticker", "profit_loss"],
        title="Retorno Percentual vs Valor Total",
        labels={"total_value": "Valor (R$)", "profit_loss_pct": "Retorno (%)"},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)


def show_treemap(df: pd.DataFrame) -> None:
    """Show treemap visualization."""
    st.subheader("🗺️ Treemap do Portfolio")

    # Treemap by source and ticker
    fig = px.treemap(
        df,
        path=["source", "ticker"],
        values="total_value",
        title="Hierarquia: Fonte → Ticker",
        color="total_value",
        color_continuous_scale="RdYlGn",
        hover_data=["quantity", "avg_price", "current_price"],
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Treemap by asset class (if available)
    if "asset_class" in df.columns and "category" in df.columns:
        fig = px.treemap(
            df,
            path=["asset_class", "category", "ticker"],
            values="total_value",
            title="Hierarquia: Classe → Categoria → Ticker",
            color="total_value",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)


def show_concentration_analysis(df: pd.DataFrame) -> None:
    """Show portfolio concentration analysis."""
    st.subheader("📈 Análise de Concentração")

    # Calculate cumulative percentage
    df_sorted = df.sort_values("total_value", ascending=False).copy()
    df_sorted["cumulative_value"] = df_sorted["total_value"].cumsum()
    total_value = df_sorted["total_value"].sum()
    df_sorted["cumulative_pct"] = (df_sorted["cumulative_value"] / total_value) * 100
    df_sorted["rank"] = range(1, len(df_sorted) + 1)

    # Concentration metrics
    col1, col2, col3 = st.columns(3)

    top_5_pct = df_sorted.head(5)["total_value"].sum() / total_value * 100
    top_10_pct = df_sorted.head(10)["total_value"].sum() / total_value * 100
    top_20_pct = df_sorted.head(20)["total_value"].sum() / total_value * 100

    with col1:
        st.metric("Top 5 Ativos", f"{top_5_pct:.1f}%", help="Concentração nos 5 maiores ativos")
    with col2:
        st.metric("Top 10 Ativos", f"{top_10_pct:.1f}%", help="Concentração nos 10 maiores ativos")
    with col3:
        st.metric("Top 20 Ativos", f"{top_20_pct:.1f}%", help="Concentração nos 20 maiores ativos")

    # Concentration warning
    if top_5_pct > 50:
        st.warning(
            f"⚠️ **Alta concentração!** Os 5 maiores ativos representam {top_5_pct:.1f}% "
            f"do portfolio. Considere diversificar."
        )
    elif top_5_pct > 30:
        st.info(
            f"ℹ️ **Concentração moderada.** Os 5 maiores ativos representam {top_5_pct:.1f}% "
            f"do portfolio."
        )
    else:
        st.success(
            f"✅ **Boa diversificação!** Os 5 maiores ativos representam apenas {top_5_pct:.1f}% "
            f"do portfolio."
        )

    # Cumulative distribution curve
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_sorted["rank"],
            y=df_sorted["cumulative_pct"],
            mode="lines+markers",
            name="Concentração Acumulada",
            line=dict(color="blue", width=2),
            marker=dict(size=6),
        )
    )

    # Add 80/20 reference line
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="red",
        annotation_text="80% do portfolio",
    )

    fig.update_layout(
        title="Curva de Concentração do Portfolio",
        xaxis_title="Ranking (por valor)",
        yaxis_title="% Acumulado do Portfolio",
        hovermode="x unified",
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Find how many assets make up 80%
    assets_for_80 = len(df_sorted[df_sorted["cumulative_pct"] <= 80])
    st.info(
        f"📊 **{assets_for_80} ativos** (de {len(df)}) representam 80% do valor total do portfolio"
    )

    # Top assets table
    with st.expander("📋 Ver Top 20 Ativos"):
        top_20 = df_sorted.head(20)[
            ["ticker", "total_value", "cumulative_pct", "source"]
        ].copy()
        top_20.columns = ["Ticker", "Valor (R$)", "% Acumulado", "Fonte"]
        st.dataframe(top_20, use_container_width=True, hide_index=True)
