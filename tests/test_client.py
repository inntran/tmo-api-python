"""Tests for TMOClient."""

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from tmo_api._version import __version__
from tmo_api.client import TMOClient
from tmo_api.environments import Environment
from tmo_api.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
)


class TestClientInitialization:
    """Test client initialization."""

    def test_client_init_with_defaults(self, mock_token, mock_database):
        """Test client initialization with default values."""
        client = TMOClient(token=mock_token, database=mock_database)
        assert client.token == mock_token
        assert client.database == mock_database
        assert client.base_url == Environment.US.value
        assert client.timeout == 30
        assert client.debug is False

    def test_client_init_with_environment_enum(self, mock_token, mock_database):
        """Test client initialization with environment enum."""
        client = TMOClient(
            token=mock_token,
            database=mock_database,
            environment=Environment.CANADA,
        )
        assert client.base_url == Environment.CANADA.value

    def test_client_init_with_custom_url(self, mock_token, mock_database):
        """Test client initialization with custom URL string."""
        custom_url = "https://custom-api.example.com"
        client = TMOClient(
            token=mock_token,
            database=mock_database,
            environment=custom_url,
        )
        assert client.base_url == custom_url

    def test_client_init_with_custom_timeout(self, mock_token, mock_database):
        """Test client initialization with custom timeout."""
        client = TMOClient(
            token=mock_token,
            database=mock_database,
            timeout=60,
        )
        assert client.timeout == 60

    def test_client_init_with_debug(self, mock_token, mock_database):
        """Test client initialization with debug mode."""
        client = TMOClient(
            token=mock_token,
            database=mock_database,
            debug=True,
        )
        assert client.debug is True

    def test_client_session_headers(self, mock_token, mock_database):
        """Test session headers are set correctly."""
        client = TMOClient(token=mock_token, database=mock_database)
        assert client.session.headers["Token"] == mock_token
        assert client.session.headers["Database"] == mock_database
        assert client.session.headers["Content-Type"] == "application/json"
        assert (
            client.session.headers["User-Agent"]
            == f"python-tmo-api/{__version__} (https://inntran.github.io/tmo-api-python/)"
        )

    def test_client_custom_user_agent(self, mock_token, mock_database):
        """Test providing a custom user agent for the session."""
        custom_agent = "custom-agent/1.0"
        client = TMOClient(token=mock_token, database=mock_database, user_agent=custom_agent)
        assert client.session.headers["User-Agent"] == custom_agent

    def test_client_resources_initialized(self, mock_token, mock_database):
        """Test that all resource objects are initialized."""
        client = TMOClient(token=mock_token, database=mock_database)

        # Shares resources
        assert hasattr(client, "shares_pools")
        assert hasattr(client, "shares_partners")
        assert hasattr(client, "shares_distributions")
        assert hasattr(client, "shares_certificates")
        assert hasattr(client, "shares_history")

        # Capital resources
        assert hasattr(client, "capital_pools")
        assert hasattr(client, "capital_partners")
        assert hasattr(client, "capital_distributions")
        assert hasattr(client, "capital_history")


class TestClientRequests:
    """Test client HTTP request methods."""

    @patch("tmo_api.client.requests.Session.request")
    def test_get_request_success(
        self, mock_request, mock_token, mock_database, mock_api_response_success
    ):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response_success
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = TMOClient(token=mock_token, database=mock_database)
        result = client.get("test/endpoint")

        assert result == mock_api_response_success
        mock_request.assert_called_once()

    @patch("tmo_api.client.requests.Session.request")
    def test_post_request_success(
        self, mock_request, mock_token, mock_database, mock_api_response_success
    ):
        """Test successful POST request."""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response_success
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = TMOClient(token=mock_token, database=mock_database)
        result = client.post("test/endpoint", json={"key": "value"})

        assert result == mock_api_response_success

    @patch("tmo_api.client.requests.Session.request")
    def test_put_request_success(
        self, mock_request, mock_token, mock_database, mock_api_response_success
    ):
        """Test successful PUT request."""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response_success
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = TMOClient(token=mock_token, database=mock_database)
        result = client.put("test/endpoint", json={"key": "value"})

        assert result == mock_api_response_success

    @patch("tmo_api.client.requests.Session.request")
    def test_delete_request_success(
        self, mock_request, mock_token, mock_database, mock_api_response_success
    ):
        """Test successful DELETE request."""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response_success
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = TMOClient(token=mock_token, database=mock_database)
        result = client.delete("test/endpoint")

        assert result == mock_api_response_success


class TestClientErrors:
    """Test client error handling."""

    @patch("tmo_api.client.requests.Session.request")
    def test_api_error_response(
        self, mock_request, mock_token, mock_database, mock_api_response_error
    ):
        """Test handling of API error response."""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response_error
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = TMOClient(token=mock_token, database=mock_database)

        with pytest.raises(APIError) as exc_info:
            client.get("test/endpoint")

        assert str(exc_info.value) == "Test error message"
        assert exc_info.value.error_number == 500

    @patch("tmo_api.client.requests.Session.request")
    def test_authentication_error_401(self, mock_request, mock_token, mock_database):
        """Test handling of 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_request.return_value = mock_response

        client = TMOClient(token=mock_token, database=mock_database)

        with pytest.raises(AuthenticationError) as exc_info:
            client.get("test/endpoint")

        assert "Invalid token or database" in str(exc_info.value)

    @patch("tmo_api.client.requests.Session.request")
    def test_authentication_error_403(self, mock_request, mock_token, mock_database):
        """Test handling of 403 forbidden error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_request.return_value = mock_response

        client = TMOClient(token=mock_token, database=mock_database)

        with pytest.raises(AuthenticationError) as exc_info:
            client.get("test/endpoint")

        assert "Access denied" in str(exc_info.value)

    @patch("tmo_api.client.requests.Session.request")
    def test_timeout_error(self, mock_request, mock_token, mock_database):
        """Test handling of timeout error."""
        mock_request.side_effect = requests.exceptions.Timeout()

        client = TMOClient(token=mock_token, database=mock_database)

        with pytest.raises(NetworkError) as exc_info:
            client.get("test/endpoint")

        assert "timed out" in str(exc_info.value)

    @patch("tmo_api.client.requests.Session.request")
    def test_connection_error(self, mock_request, mock_token, mock_database):
        """Test handling of connection error."""
        mock_request.side_effect = requests.exceptions.ConnectionError()

        client = TMOClient(token=mock_token, database=mock_database)

        with pytest.raises(NetworkError) as exc_info:
            client.get("test/endpoint")

        assert "Connection error" in str(exc_info.value)

    @patch("tmo_api.client.requests.Session.request")
    def test_invalid_json_response(self, mock_request, mock_token, mock_database):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = TMOClient(token=mock_token, database=mock_database)

        with pytest.raises(APIError) as exc_info:
            client.get("test/endpoint")

        assert "Invalid JSON" in str(exc_info.value)


class TestClientDebug:
    """Test client debug logging."""

    def test_debug_log_disabled(self, mock_token, mock_database, capsys):
        """Test debug logging is disabled by default."""
        client = TMOClient(token=mock_token, database=mock_database, debug=False)
        client._debug_log("Test message")

        captured = capsys.readouterr()
        assert "Test message" not in captured.err

    def test_debug_log_enabled(self, mock_token, mock_database, capsys):
        """Test debug logging when enabled."""
        client = TMOClient(token=mock_token, database=mock_database, debug=True)
        client._debug_log("Test message")

        captured = capsys.readouterr()
        assert "DEBUG: Test message" in captured.err
