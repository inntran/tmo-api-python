"""Base models for The Mortgage Office SDK."""

from datetime import datetime
from typing import Any, Dict, Optional


class BaseResponse:
    """Base response model for API responses."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize response from API data.

        Args:
            data: Raw API response data
        """
        self.raw_data: Dict[str, Any] = data
        self.data: Dict[str, Any] = data.get("Data") or {}
        self.error_message: Optional[str] = data.get("ErrorMessage")
        self.error_number: Optional[int] = data.get("ErrorNumber")
        self.status: int = data.get("Status", 0)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(status={self.status})"


class BaseModel:
    """Base model for API data objects."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize model from API data.

        Args:
            data: Raw API data for this object
        """
        self.raw_data: Dict[str, Any] = data
        self._parse_data(data)

    def _parse_data(self, data: Dict[str, Any]) -> None:
        """Parse raw API data into model attributes.

        Args:
            data: Raw API data
        """
        # Set basic attributes from data, preserving original field names
        for key, value in data.items():
            # Use the original field name as-is
            setattr(self, key, value)

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case.

        Args:
            name: CamelCase string

        Returns:
            snake_case string
        """
        result: list[str] = []
        for i, c in enumerate(name):
            if c.isupper() and i > 0:
                result.append("_")
            result.append(c.lower())
        return "".join(result)

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object.

        Args:
            date_str: Date string from API

        Returns:
            Parsed datetime or None
        """
        if not date_str:
            return None

        # Try common date formats
        formats: list[str] = [
            "%m/%d/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # If no format matches, return None
        return None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({getattr(self, 'rec_id', 'unknown')})"
