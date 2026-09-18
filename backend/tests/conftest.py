"""Test configuration and fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up test environment variables."""
    monkeypatch.setenv(
        "SWISSCOM_API_KEY",
        os.environ.get("SWISSCOM_API_KEY", "test_key_for_tests"),
    )
    monkeypatch.setenv(
        "SWISSCOM_BASE_URL",
        os.environ.get("SWISSCOM_BASE_URL", "https://example.invalid/v1"),
    )
    monkeypatch.setenv(
        "SWISSCOM_MODEL",
        os.environ.get("SWISSCOM_MODEL", "test-model"),
    )
