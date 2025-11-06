"""Tests for exception classes."""

import pytest

from tmo_api.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    TMOException,
    ValidationError,
)


class TestExceptions:
    """Test custom exception classes."""

    def test_base_exception(self):
        """Test TMOException base exception."""
        error = TMOException("Test error", error_number=123)
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.error_number == 123

    def test_base_exception_without_error_number(self):
        """Test base exception without error number."""
        error = TMOException("Test error")
        assert error.message == "Test error"
        assert error.error_number is None

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid credentials")
        assert isinstance(error, TMOException)
        assert str(error) == "Invalid credentials"

    def test_api_error(self):
        """Test APIError."""
        error = APIError("API returned error", error_number=500)
        assert isinstance(error, TMOException)
        assert error.message == "API returned error"
        assert error.error_number == 500

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid input")
        assert isinstance(error, TMOException)
        assert str(error) == "Invalid input"

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("Connection failed")
        assert isinstance(error, TMOException)
        assert str(error) == "Connection failed"

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from base exception."""
        assert issubclass(AuthenticationError, TMOException)
        assert issubclass(APIError, TMOException)
        assert issubclass(ValidationError, TMOException)
        assert issubclass(NetworkError, TMOException)
