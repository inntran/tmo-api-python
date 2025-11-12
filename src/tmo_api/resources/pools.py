"""Pools resource for The Mortgage Office SDK."""

from enum import Enum
from typing import TYPE_CHECKING, Any, List, cast

from ..models.pool import Pool, PoolResponse, PoolsResponse

if TYPE_CHECKING:
    from ..client import TMOClient


class PoolType(Enum):
    """Pool types supported by the API."""

    SHARES = "Shares"
    CAPITAL = "Capital"


class PoolsResource:
    """Resource for managing mortgage pools."""

    def __init__(self, client: "TMOClient", pool_type: PoolType = PoolType.SHARES) -> None:
        """Initialize the pools resource.

        Args:
            client: The base client instance
            pool_type: The type of pool (Shares or Capital)
        """
        self.client = client
        self.pool_type = pool_type
        self.base_path = f"LSS.svc/{pool_type.value}"

    def get_pool(self, account: str) -> Pool:
        """Get pool details by account.

        Args:
            account: The pool account identifier

        Returns:
            Pool object with detailed information

        Raises:
            APIError: If the API returns an error
            ValidationError: If account is invalid
        """
        if not account:
            from ..exceptions import ValidationError

            raise ValidationError("Account parameter is required")

        endpoint = f"{self.base_path}/Pools/{account}"
        response_data = self.client.get(endpoint)
        response = PoolResponse(response_data)
        return response.pool  # type: ignore

    def get_pool_partners(self, account: str) -> list:
        """Get pool partners by account.

        Returns comprehensive financial and contact information for all partners
        associated with a specific pool, including capital activity and performance metrics.

        Args:
            account: The pool account identifier

        Returns:
            List of partner dictionaries (CPartners:#TmoAPI), each containing:

            Financial Information:
            - BegCapital: Beginning capital balance
            - Contributions: Capital contributions made by the partner
            - Distributions: Distributions paid out to the partner
            - EndCapital: Ending capital balance for the partner
            - Income: Income earned
            - Withdrawals: Withdrawal amounts
            - WithdrawalsAndDisbursements: Total withdrawals and disbursements
            - IRR: Internal Rate of Return

            Contact Information:
            - Account: Partner account identifier
            - SortName: Partner's name
            - Address: Street, City, State, ZipCode
            - Phone: PhoneHome, PhoneWork, PhoneCell, PhoneFax
            - EmailAddress: Partner's email
            - TIN: Tax Identification Number

            Other:
            - AccountType: Type of account
            - ERISA: ERISA flag
            - IsACH: ACH flag
            - RecID: Unique record identifier

            Note: This combines both financial data and contact information, unlike
            partners.get_partner() which only has contact/profile info without transactions.

        Raises:
            APIError: If the API returns an error
            ValidationError: If account is invalid
        """
        if not account:
            from ..exceptions import ValidationError

            raise ValidationError("Account parameter is required")

        endpoint = f"{self.base_path}/Pools/{account}/Partners"
        response_data = self.client.get(endpoint)
        return cast(List[Any], response_data.get("Data", []))

    def get_pool_loans(self, account: str) -> list:
        """Get pool loans by account.

        Args:
            account: The pool account identifier

        Returns:
            List of pool loans

        Raises:
            APIError: If the API returns an error
            ValidationError: If account is invalid
        """
        if not account:
            from ..exceptions import ValidationError

            raise ValidationError("Account parameter is required")

        endpoint = f"{self.base_path}/Pools/{account}/Loans"
        response_data = self.client.get(endpoint)
        return cast(List[Any], response_data.get("Data", []))

    def get_pool_bank_accounts(self, account: str) -> list:
        """Get pool bank accounts by account.

        Args:
            account: The pool account identifier

        Returns:
            List of pool bank accounts

        Raises:
            APIError: If the API returns an error
            ValidationError: If account is invalid
        """
        if not account:
            from ..exceptions import ValidationError

            raise ValidationError("Account parameter is required")

        endpoint = f"{self.base_path}/Pools/{account}/BankAccounts"
        response_data = self.client.get(endpoint)
        return cast(List[Any], response_data.get("Data", []))

    def get_pool_attachments(self, account: str) -> list:
        """Get pool attachments by account.

        Args:
            account: The pool account identifier

        Returns:
            List of pool attachments

        Raises:
            APIError: If the API returns an error
            ValidationError: If account is invalid
        """
        if not account:
            from ..exceptions import ValidationError

            raise ValidationError("Account parameter is required")

        endpoint = f"{self.base_path}/Pools/{account}/Attachments"
        response_data = self.client.get(endpoint)
        return cast(List[Any], response_data.get("Data", []))

    def list_all(self) -> List[Pool]:
        """List all pools.

        Returns:
            List of all pools

        Raises:
            APIError: If the API returns an error
        """
        endpoint = f"{self.base_path}/Pools"
        response_data = self.client.get(endpoint)
        response = PoolsResponse(response_data)
        return response.pools
