"""
End-to-end tests for the Streamlit GUI using Playwright.

These tests verify the functionality of the web interface including:
- Navigation between pages
- File upload and consolidation
- Data visualization rendering
- Report generation and export
"""

import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def app_url():
    """Base URL for the Streamlit application."""
    return "http://localhost:8501"


class TestNavigation:
    """Test suite for page navigation."""

    def test_home_page_loads(self, page: Page, app_url: str) -> None:
        """Test that the home page loads successfully."""
        page.goto(app_url)
        page.wait_for_load_state("networkidle")

        # Check for title
        expect(page.locator("h1")).to_contain_text("Portfolio Analysis")

    def test_sidebar_navigation(self, page: Page, app_url: str) -> None:
        """Test sidebar navigation to all pages."""
        page.goto(app_url)
        page.wait_for_load_state("networkidle")

        # List of page labels to test
        pages = [
            "🏠 Home",
            "🔄 Consolidação",
            "📈 Visualizações",
            "📊 Comparação",
            "📄 Relatórios",
        ]

        for page_name in pages:
            # Click on page in sidebar
            page.get_by_text(page_name).click()
            time.sleep(1)  # Wait for page transition

            # Verify page loaded
            page.wait_for_load_state("networkidle")

    def test_sidebar_about_section(self, page: Page, app_url: str) -> None:
        """Test that sidebar about section is visible."""
        page.goto(app_url)
        page.wait_for_load_state("networkidle")

        # Check for "Sobre" section in sidebar
        expect(page.get_by_text("ℹ️ Sobre")).to_be_visible()
        expect(page.get_by_text("B3")).to_be_visible()
        expect(page.get_by_text("Kinvo")).to_be_visible()


class TestConsolidationPage:
    """Test suite for the consolidation page."""

    def test_consolidation_page_loads(self, page: Page, app_url: str) -> None:
        """Test that consolidation page loads correctly."""
        page.goto(app_url)
        page.wait_for_load_state("networkidle")

        # Navigate to consolidation
        page.get_by_text("🔄 Consolidação").click()
        page.wait_for_load_state("networkidle")

        # Check for upload section
        expect(page.locator("h2")).to_contain_text("Upload de Planilhas")

    def test_file_upload_widgets_present(self, page: Page, app_url: str) -> None:
        """Test that file upload widgets are present."""
        page.goto(app_url)
        page.get_by_text("🔄 Consolidação").click()
        page.wait_for_load_state("networkidle")

        # Check for file upload labels
        expect(page.get_by_text("B3 Carteira")).to_be_visible()
        expect(page.get_by_text("Kinvo Carteira")).to_be_visible()
        expect(page.get_by_text("MyProfit Carteira")).to_be_visible()
        expect(page.get_by_text("XP Carteira")).to_be_visible()

    def test_deduplication_strategy_selector(self, page: Page, app_url: str) -> None:
        """Test deduplication strategy selector."""
        page.goto(app_url)
        page.get_by_text("🔄 Consolidação").click()
        page.wait_for_load_state("networkidle")

        # Check for strategy selector
        expect(page.get_by_text("Estratégia de Deduplicação")).to_be_visible()

    def test_consolidation_button_disabled_without_files(self, page: Page, app_url: str) -> None:
        """Test that consolidation requires at least one file."""
        page.goto(app_url)
        page.get_by_text("🔄 Consolidação").click()
        page.wait_for_load_state("networkidle")

        # Should show warning about no files
        expect(page.get_by_text("Nenhum arquivo carregado ainda")).to_be_visible()


class TestVisualizationsPage:
    """Test suite for visualizations page."""

    def test_visualizations_page_loads(self, page: Page, app_url: str) -> None:
        """Test that visualizations page loads."""
        page.goto(app_url)
        page.get_by_text("📈 Visualizações").click()
        page.wait_for_load_state("networkidle")

        # Check for page title
        expect(page.locator("h1")).to_contain_text("Visualizações Interativas")

    def test_visualization_tabs_present(self, page: Page, app_url: str) -> None:
        """Test that visualization tabs are present."""
        page.goto(app_url)
        page.get_by_text("📈 Visualizações").click()
        page.wait_for_load_state("networkidle")

        # If portfolio exists, check for tabs
        if not page.get_by_text("Nenhum portfolio consolidado").is_visible():
            expect(page.get_by_text("📊 Distribuição")).to_be_visible()
            expect(page.get_by_text("🏆 Top Holdings")).to_be_visible()

    def test_filters_present(self, page: Page, app_url: str) -> None:
        """Test that filters are present in sidebar."""
        page.goto(app_url)
        page.get_by_text("📈 Visualizações").click()
        page.wait_for_load_state("networkidle")

        # Check for filters in sidebar (if portfolio exists)
        if not page.get_by_text("Nenhum portfolio consolidado").is_visible():
            expect(page.get_by_text("🔍 Filtros")).to_be_visible()


class TestComparisonPage:
    """Test suite for version comparison page."""

    def test_comparison_page_loads(self, page: Page, app_url: str) -> None:
        """Test that comparison page loads."""
        page.goto(app_url)
        page.get_by_text("📊 Comparação").click()
        page.wait_for_load_state("networkidle")

        # Check for page title
        expect(page.locator("h1")).to_contain_text("Comparação de Versões")

    def test_version_selectors_present(self, page: Page, app_url: str) -> None:
        """Test that version selectors are present."""
        page.goto(app_url)
        page.get_by_text("📊 Comparação").click()
        page.wait_for_load_state("networkidle")

        # If versions exist, check for selectors
        if not page.get_by_text("Nenhuma versão consolidada").is_visible():
            expect(page.get_by_text("Versão 1")).to_be_visible()
            expect(page.get_by_text("Versão 2")).to_be_visible()


class TestReportsPage:
    """Test suite for reports page."""

    def test_reports_page_loads(self, page: Page, app_url: str) -> None:
        """Test that reports page loads."""
        page.goto(app_url)
        page.get_by_text("📄 Relatórios").click()
        page.wait_for_load_state("networkidle")

        # Check for page title
        expect(page.locator("h1")).to_contain_text("Relatórios e Exportações")

    def test_report_type_selection(self, page: Page, app_url: str) -> None:
        """Test report type selection options."""
        page.goto(app_url)
        page.get_by_text("📄 Relatórios").click()
        page.wait_for_load_state("networkidle")

        # If portfolio exists, check for report types
        if not page.get_by_text("Nenhum portfolio consolidado").is_visible():
            expect(page.get_by_text("📋 Relatório Executivo")).to_be_visible()
            expect(page.get_by_text("📈 Análise de Performance")).to_be_visible()

    def test_export_buttons_present(self, page: Page, app_url: str) -> None:
        """Test that export buttons are present."""
        page.goto(app_url)
        page.get_by_text("📄 Relatórios").click()
        page.wait_for_load_state("networkidle")

        # If portfolio exists, check for export options
        if not page.get_by_text("Nenhum portfolio consolidado").is_visible():
            # Wait for report to generate
            time.sleep(2)
            # Export buttons should be present
            expect(page.get_by_text("Exportar")).to_be_visible()


class TestResponsiveness:
    """Test suite for responsive design."""

    @pytest.mark.parametrize(
        "viewport",
        [
            {"width": 1920, "height": 1080},  # Desktop
            {"width": 1366, "height": 768},  # Laptop
            {"width": 768, "height": 1024},  # Tablet
        ],
    )
    def test_layout_at_different_viewports(
        self, page: Page, app_url: str, viewport: dict
    ) -> None:
        """Test layout at different viewport sizes."""
        page.set_viewport_size(viewport)
        page.goto(app_url)
        page.wait_for_load_state("networkidle")

        # Basic layout should work at all sizes
        expect(page.locator("h1")).to_be_visible()


class TestPerformance:
    """Test suite for performance metrics."""

    def test_page_load_time(self, page: Page, app_url: str) -> None:
        """Test that page loads within acceptable time."""
        start_time = time.time()
        page.goto(app_url)
        page.wait_for_load_state("networkidle")
        load_time = time.time() - start_time

        # Page should load within 10 seconds
        assert load_time < 10, f"Page took {load_time:.2f}s to load (should be < 10s)"

    def test_navigation_speed(self, page: Page, app_url: str) -> None:
        """Test that navigation between pages is fast."""
        page.goto(app_url)
        page.wait_for_load_state("networkidle")

        pages = ["🔄 Consolidação", "📈 Visualizações", "📊 Comparação"]

        for page_name in pages:
            start_time = time.time()
            page.get_by_text(page_name).click()
            page.wait_for_load_state("networkidle")
            nav_time = time.time() - start_time

            # Navigation should be fast (< 3 seconds)
            assert nav_time < 3, f"Navigation to {page_name} took {nav_time:.2f}s"


class TestAccessibility:
    """Test suite for accessibility features."""

    def test_page_has_title(self, page: Page, app_url: str) -> None:
        """Test that page has a proper title."""
        page.goto(app_url)
        page.wait_for_load_state("networkidle")

        # Check for page title
        title = page.title()
        assert "Portfolio" in title, f"Page title '{title}' should contain 'Portfolio'"

    def test_headings_hierarchy(self, page: Page, app_url: str) -> None:
        """Test that headings are properly structured."""
        page.goto(app_url)
        page.wait_for_load_state("networkidle")

        # Should have at least one h1
        h1_count = page.locator("h1").count()
        assert h1_count >= 1, "Page should have at least one H1 heading"


# Marks for running specific test suites
pytestmark = [
    pytest.mark.e2e,  # Mark all tests as e2e
    pytest.mark.slow,  # Mark all tests as slow (requires running Streamlit server)
]
