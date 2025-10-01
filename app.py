"""
Streamlit Web Application for Investment Portfolio Analysis.

Main entry point for the web-based portfolio analysis system.
"""

import sys
from pathlib import Path

import streamlit as st

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="Portfolio Analysis System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/adrianolucasdepaula/claude_projects",
        "Report a bug": "https://github.com/adrianolucasdepaula/claude_projects/issues",
        "About": """
        # Portfolio Analysis System

        Sistema de análise e consolidação de portfolios de investimentos.

        **Versão:** 1.0.0

        **Desenvolvido com:**
        - Python 3.13
        - Streamlit
        - Pandas
        - Plotly
        """,
    },
)


def main() -> None:
    """Main application entry point."""
    # Sidebar navigation
    st.sidebar.title("📊 Portfolio Analysis")
    st.sidebar.markdown("---")

    # Navigation
    page = st.sidebar.radio(
        "Navegação",
        [
            "🏠 Home",
            "🔄 Consolidação",
            "📈 Visualizações",
            "📊 Comparação",
            "📄 Relatórios",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Sobre")
    st.sidebar.info(
        """
        Sistema de consolidação e análise de portfolios de investimentos.

        **Fontes suportadas:**
        - B3
        - Kinvo
        - MyProfit
        - XP
        """
    )

    # Route to appropriate page
    if page == "🏠 Home":
        from src.invest.gui.pages import home

        home.show()
    elif page == "🔄 Consolidação":
        from src.invest.gui.pages import consolidation

        consolidation.show()
    elif page == "📈 Visualizações":
        from src.invest.gui.pages import visualizations

        visualizations.show()
    elif page == "📊 Comparação":
        from src.invest.gui.pages import comparison

        comparison.show()
    elif page == "📄 Relatórios":
        from src.invest.gui.pages import reports

        reports.show()


if __name__ == "__main__":
    main()
