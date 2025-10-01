"""Playwright configuration for pytest."""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context arguments."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "locale": "pt-BR",
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments."""
    return {
        **browser_type_launch_args,
        "headless": True,  # Set to False for debugging
        "slow_mo": 100,  # Slow down operations by 100ms for visibility
    }


@pytest.fixture
def base_url():
    """Base URL for the Streamlit application."""
    return "http://localhost:8501"
