"""Custom exceptions for The Mortgage Office SDK."""

from typing import Optional


class TMOException(Exception):
    """Base exception for The Mortgage Office SDK."""

    def __init__(self, message: str, error_number: Optional[int] = None) -> None:
        super().__init__(message)
        self.message: str = message
        self.error_number: Optional[int] = error_number


class AuthenticationError(TMOException):
    """Raised when authentication fails."""

    pass


class APIError(TMOException):
    """Raised when the API returns an error response."""

    pass


class ValidationError(TMOException):
    """Raised when request validation fails."""

    pass


class NetworkError(TMOException):
    """Raised when network-related errors occur."""

    pass
