"""Partners resource for The Mortgage Office SDK."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from .pools import PoolType

if TYPE_CHECKING:
    from ..client import TMOClient


class PartnersResource:
    """Resource for managing pool partners."""

    def __init__(self, client: "TMOClient", pool_type: PoolType = PoolType.SHARES) -> None:
        """Initialize the partners resource.

        Args:
            client: The base client instance
            pool_type: The type of pool (Shares or Capital)
        """
        self.client = client
        self.pool_type = pool_type
        self.base_path = f"LSS.svc/{pool_type.value}"

    def get_partner(self, account: str) -> Dict[str, Any]:
        """Get partner details by Account.

        Returns a single partner with complete profile information including contact details,
        ACH banking information, custom fields, and trustee information.

        Args:
            account: The partner account identifier

        Returns:
            Partner data dictionary (CPartner:#TmoAPI) containing:
            - Contact information: Name, address, phone, email
            - ACH details: Bank account, routing number, ACH settings
            - CustomFields: Account-specific custom field values
            - Trustee info: TrusteeRecID, TrusteeAccountRef, TrusteeAccountType
            - Tax info: TIN, TINType
            - Delivery options, statement preferences, and other settings

            Note: Does NOT include financial transactions (Contributions/Distributions).
            Use pools.get_pool_partners() for financial data.

        Raises:
            APIError: If the API returns an error
            ValidationError: If account is invalid
        """
        if not account:
            from ..exceptions import ValidationError

            raise ValidationError("Account parameter is required")

        endpoint = f"{self.base_path}/Partners/{account}"
        response_data = self.client.get(endpoint)
        return cast(Dict[str, Any], response_data.get("Data", {}))

    def get_partner_attachments(self, account: str) -> List[Any]:
        """Get partner attachments by Account.

        Args:
            account: The partner account identifier

        Returns:
            List of partner attachments

        Raises:
            APIError: If the API returns an error
            ValidationError: If account is invalid
        """
        if not account:
            from ..exceptions import ValidationError

            raise ValidationError("Account parameter is required")

        endpoint = f"{self.base_path}/Partners/{account}/Attachments"
        response_data = self.client.get(endpoint)
        return cast(List[Any], response_data.get("Data", []))

    def list_all(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Any]:
        """List all partners with optional date filtering.

        Returns a list of partners with profile information. Date range filters
        partners based on DateCreated and LastChanged timestamps.

        Args:
            start_date: Start date for filtering (MM/DD/YYYY format)
            end_date: End date for filtering (MM/DD/YYYY format)

        Returns:
            List of partner dictionaries (CPSSPartners:#TmoAPI), each containing:
            - Account: Partner account identifier
            - Contact info: FirstName, LastName, MI, SortName, Address (Street, City, State, ZipCode)
            - Phone: PhoneHome, PhoneWork, PhoneCell, PhoneFax, PhoneMain
            - Email: EmailAddress
            - CustomFields: Account-specific custom field values (e.g., Account Type, Interest Rate, Principal Amount)
            - Trustee info: TrusteeName, TrusteeAccount, TrusteeAccountRef, TrusteeAccountType
            - Tax info: TIN
            - Flags: ERISA, IsACH, UsePayee
            - Timestamps: DateCreated, LastChanged
            - RecID: Unique record identifier

        Raises:
            APIError: If the API returns an error
            ValidationError: If date format is invalid
        """
        endpoint = f"{self.base_path}/Partners"
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
