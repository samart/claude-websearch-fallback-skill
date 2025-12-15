"""Pytest configuration and fixtures."""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires Chrome)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-integration"):
        # Run all tests including integration
        return

    skip_integration = pytest.mark.skip(reason="Need --run-integration to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
