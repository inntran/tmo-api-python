# Testing

The SDK uses pytest for testing with 92% code coverage.

## Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_client.py

# Specific test
pytest tests/test_client.py::TestClientInitialization::test_client_init_with_defaults

# With verbose output
pytest -v

# With coverage
pytest --cov=tmo_api --cov-report=term
```

## Writing Tests

Tests use pytest fixtures and mocking:

```python
import os
import pytest
from unittest.mock import patch, MagicMock
from tmo_api import TMOClient

@pytest.fixture
def client():
    """Create a test client using environment variables."""
    return TMOClient(
        token=os.environ.get("TMO_API_TOKEN", "test-token"),
        database=os.environ.get("TMO_DATABASE", "test-db")
    )

def test_example(client):
    with patch('requests.Session.request') as mock_request:
        mock_request.return_value.json.return_value = {"Status": 0, "Data": []}
        mock_request.return_value.raise_for_status.return_value = None
        result = client.shares_pools.list_all()
        assert isinstance(result, list)
```
