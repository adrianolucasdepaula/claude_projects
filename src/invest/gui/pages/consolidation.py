"""Consolidation page with file upload and deduplication configuration."""

import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def show() -> None:
    """Display the consolidation page."""
    st.title("🔄 Consolidação de Portfolios")
    st.markdown("---")

    st.markdown(
        """
        **Faça upload das suas planilhas de portfolio** para consolidar em um único arquivo.

        Fontes suportadas: **B3**, **Kinvo**, **MyProfit**, **XP**
        """
    )

    # File upload section
    st.subheader("📤 Upload de Planilhas")

    col1, col2 = st.columns(2)

    with col1:
        b3_file = st.file_uploader(
            "B3 Carteira (.xlsx)",
            type=["xlsx"],
            key="b3",
            help="Planilha exportada da B3",
        )

        kinvo_file = st.file_uploader(
            "Kinvo Carteira (.xlsx)",
            type=["xlsx"],
            key="kinvo",
            help="Planilha exportada do Kinvo",
        )

    with col2:
        myprofit_file = st.file_uploader(
            "MyProfit Carteira (.xls)",
            type=["xls"],
            key="myprofit",
            help="Planilha exportada do MyProfit",
        )

        xp_file = st.file_uploader(
            "XP Carteira (.xlsx)",
            type=["xlsx"],
            key="xp",
            help="Planilha exportada da XP",
        )

    # Count uploaded files
    uploaded_files = {
        "B3": b3_file,
        "Kinvo": kinvo_file,
        "MyProfit": myprofit_file,
        "XP": xp_file,
    }
    num_uploaded = sum(1 for f in uploaded_files.values() if f is not None)

    if num_uploaded > 0:
        st.success(f"✅ {num_uploaded} arquivo(s) carregado(s)")
    else:
        st.info("📁 Nenhum arquivo carregado ainda")

    st.markdown("---")

    # Configuration section
    st.subheader("⚙️ Configuração da Consolidação")

    col1, col2 = st.columns(2)

    with col1:
        dedup_strategy = st.selectbox(
            "Estratégia de Deduplicação",
            options=["aggregate", "prioritize", "latest"],
            format_func=lambda x: {
                "aggregate": "Agregar (somar quantidades)",
                "prioritize": "Priorizar (por fonte)",
                "latest": "Mais recente",
            }[x],
            help="""
            - **Agregar**: Soma as quantidades de ativos duplicados
            - **Priorizar**: Mantém apenas a fonte de maior prioridade
            - **Mais recente**: Mantém o registro mais recente
            """,
        )

    with col2:
        enable_versioning = st.checkbox(
            "Habilitar versionamento",
            value=True,
            help="Salva snapshots das consolidações para comparação histórica",
        )

    # Display priority order if prioritize strategy
    if dedup_strategy == "prioritize":
        st.info(
            """
            **Ordem de prioridade das fontes:**
            1. MyProfit (mais completo)
            2. B3 (dados oficiais)
            3. XP (corretora)
            4. Kinvo (agregador)
            """
        )

    st.markdown("---")

    # Consolidation button
    if num_uploaded == 0:
        st.warning("⚠️ Faça upload de pelo menos uma planilha para consolidar")
    else:
        if st.button("🚀 Consolidar Portfolios", type="primary", use_container_width=True):
            consolidate_portfolios(
                uploaded_files, dedup_strategy, enable_versioning
            )


def consolidate_portfolios(
    uploaded_files: dict,
    strategy: str,
    enable_versioning: bool,
) -> None:
    """
    Consolidate uploaded portfolio files.

    Args:
        uploaded_files: Dictionary of source name to uploaded file
        strategy: Deduplication strategy
        enable_versioning: Whether to enable versioning
    """
    from src.invest.analyzers.portfolio import PortfolioConsolidator

    with st.spinner("Processando portfolios..."):
        try:
            # Create temporary directory for uploaded files
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)

                # Save uploaded files
                file_paths = {}
                for source, file in uploaded_files.items():
                    if file is not None:
                        ext = ".xls" if source == "MyProfit" else ".xlsx"
                        file_path = tmpdir / f"{source.lower()}{ext}"
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        file_paths[source] = file_path

                # Create consolidator
                consolidator = PortfolioConsolidator(
                    deduplication_strategy=strategy,
                    enable_versioning=enable_versioning,
                )

                # Add portfolios
                progress_bar = st.progress(0, text="Carregando portfolios...")

                for i, (source, path) in enumerate(file_paths.items()):
                    progress_bar.progress(
                        (i + 1) / len(file_paths),
                        text=f"Carregando {source}...",
                    )

                    if source == "B3":
                        consolidator.add_b3(path)
                    elif source == "Kinvo":
                        consolidator.add_kinvo(path)
                    elif source == "MyProfit":
                        consolidator.add_myprofit(path)
                    elif source == "XP":
                        consolidator.add_xp(path)

                # Consolidate
                progress_bar.progress(1.0, text="Consolidando...")
                consolidated_df = consolidator.consolidate(
                    save=True,
                    date=datetime.now(),
                )

                progress_bar.empty()

                # Display results
                st.success("✅ Consolidação concluída com sucesso!")

                # Show deduplication stats
                dedup_info = consolidator.deduplicator.get_duplicate_info(
                    pd.concat(consolidator.portfolios, ignore_index=True)
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Registros", dedup_info["total_records"])
                with col2:
                    st.metric("Ativos Únicos", dedup_info["unique_assets"])
                with col3:
                    st.metric("Duplicatas Encontradas", dedup_info["duplicates_found"])

                if dedup_info["duplicates_found"] > 0:
                    with st.expander("🔍 Ver Duplicatas Detectadas"):
                        duplicates_df = dedup_info["duplicate_details"]
                        st.dataframe(
                            duplicates_df,
                            use_container_width=True,
                            hide_index=True,
                        )

                # Show consolidated data
                st.subheader("📊 Portfolio Consolidado")

                # Summary stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total de Ativos", len(consolidated_df))
                with col2:
                    st.metric(
                        "Valor Total",
                        f"R$ {consolidated_df['total_value'].sum():,.2f}",
                    )
                with col3:
                    if "profit_loss" in consolidated_df.columns:
                        total_pl = consolidated_df["profit_loss"].sum()
                        st.metric(
                            "Lucro/Prejuízo",
                            f"R$ {total_pl:,.2f}",
                            delta_color="normal" if total_pl >= 0 else "inverse",
                        )
                with col4:
                    st.metric("Fontes", consolidated_df["source"].nunique())

                # Data preview
                st.dataframe(
                    consolidated_df.head(20),
                    use_container_width=True,
                    hide_index=True,
                )

                # Download button
                csv = consolidated_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Portfolio Consolidado (CSV)",
                    data=csv,
                    file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        except Exception as e:
            st.error(f"❌ Erro durante a consolidação: {str(e)}")
            st.exception(e)
