"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_token():
    """Mock API token for testing."""
    return "test_token_12345"


@pytest.fixture
def mock_database():
    """Mock database name for testing."""
    return "test_database"


@pytest.fixture
def mock_pool_account():
    """Mock pool account for testing."""
    return "POOL001"


@pytest.fixture
def mock_api_response_success():
    """Mock successful API response."""
    return {
        "Status": 0,
        "ErrorMessage": None,
        "ErrorNumber": None,
        "Data": {"rec_id": 1, "account": "POOL001", "name": "Test Pool"},
    }


@pytest.fixture
def mock_api_response_error():
    """Mock error API response."""
    return {
        "Status": 1,
        "ErrorMessage": "Test error message",
        "ErrorNumber": 500,
        "Data": None,
    }


@pytest.fixture
def mock_pools_response():
    """Mock pools list response."""
    return {
        "Status": 0,
        "ErrorMessage": None,
        "ErrorNumber": None,
        "Data": [
            {"rec_id": 1, "account": "POOL001", "name": "Pool 1"},
            {"rec_id": 2, "account": "POOL002", "name": "Pool 2"},
        ],
    }
