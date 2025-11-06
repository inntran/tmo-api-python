"""Certificates resource for The Mortgage Office SDK."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from .pools import PoolType

if TYPE_CHECKING:
    from ..client import TMOClient


class CertificatesResource:
    """Resource for managing share certificates."""

    def __init__(self, client: "TMOClient", pool_type: PoolType = PoolType.SHARES) -> None:
        """Initialize the certificates resource.

        Args:
            client: The base client instance
            pool_type: The type of pool (Shares or Capital) - Note: Certificates
                are only available for Shares
        """
        self.client = client
        self.pool_type = pool_type
        self.base_path = f"LSS.svc/{pool_type.value}"

    def get_certificates(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partner_account: Optional[str] = None,
        pool_account: Optional[str] = None,
    ) -> List[Any]:
        """Get share certificates with optional filtering.

        Args:
            start_date: Start date for filtering (MM/DD/YYYY format)
            end_date: End date for filtering (MM/DD/YYYY format)
            partner_account: Partner account filter
            pool_account: Pool account filter

        Returns:
            List of share certificates

        Raises:
            APIError: If the API returns an error
            ValidationError: If date format is invalid
        """
        endpoint = f"{self.base_path}/Certificates"
        params: Dict[str, str] = {}

        if start_date:
            if not self._validate_date_format(start_date):
                from ..exceptions import ValidationError

                raise ValidationError("start_date must be in MM/DD/YYYY format")
            params["from-date"] = start_date

        if end_date:
            if not self._validate_date_format(end_date):
                from ..exceptions import ValidationError

                raise ValidationError("end_date must be in MM/DD/YYYY format")
            params["to-date"] = end_date

        if partner_account:
            params["partner-account"] = partner_account

        if pool_account:
            params["pool-account"] = pool_account

        response_data = self.client.get(endpoint, params=params if params else None)
        return cast(List[Any], response_data.get("Data", []))

    def _validate_date_format(self, date_str: str) -> bool:
        """Validate date format MM/DD/YYYY.

        Args:
            date_str: Date string to validate

        Returns:
            True if format is valid, False otherwise
        """
        try:
            from datetime import datetime

            datetime.strptime(date_str, "%m/%d/%Y")
            return True
        except ValueError:
            return False
