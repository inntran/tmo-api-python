"""History resource for The Mortgage Office SDK."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from .pools import PoolType

if TYPE_CHECKING:
    from ..client import TMOClient


class HistoryResource:
    """Resource for managing share transaction history."""

    def __init__(self, client: "TMOClient", pool_type: PoolType = PoolType.SHARES) -> None:
        """Initialize the history resource.

        Args:
            client: The base client instance
            pool_type: The type of pool (Shares or Capital)
        """
        self.client = client
        self.pool_type = pool_type
        self.base_path = f"LSS.svc/{pool_type.value}"

    def get_history(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partner_account: Optional[str] = None,
        pool_account: Optional[str] = None,
    ) -> List[Any]:
        """Get share transaction history with optional filtering.

        Returns detailed transaction records for share activities including contributions,
        withdrawals, distributions, and certificate redemptions.

        Args:
            start_date: Start date for filtering (MM/DD/YYYY format)
            end_date: End date for filtering (MM/DD/YYYY format)
            partner_account: Partner account filter
            pool_account: Pool account filter

        Returns:
            List of transaction dictionaries (CTransaction:#TmoAPI.Pss), each containing:

            Transaction Details:
            - Code: Transaction type (e.g., "PartnerWithdrawal", "Contribution", "Distribution")
            - Amount: Transaction amount (negative for withdrawals)
            - Shares: Number of shares involved (negative for redemptions)
            - SharesBalance: Remaining share balance after transaction
            - SharePrice: Price per share
            - ShareCost: Cost basis per share
            - Description: Transaction description

            Dates and Tracking:
            - DateReceived: When transaction was received
            - DateDeposited: When funds were deposited
            - DateCreated: When record was created
            - LastChanged: Last modification timestamp
            - CreatedBy: User who created the transaction

            Partner and Pool References:
            - PartnerAccount: Partner's account number
            - PartnerRecId: Partner's record ID
            - PoolAccount: Pool's account number
            - PoolRecId: Pool's record ID

            Payment Information:
            - PayAccount: Payee account number
            - PayName: Payee name
            - PayAddress: Payee address

            Certificate and ACH:
            - Certificate: Certificate number
            - ACH_BatchNumber: ACH batch number
            - ACH_TraceNumber: ACH trace number
            - ACH_TransNumber: ACH transaction number

            Other:
            - Withholding: Tax withholding amount
            - Penalty: Penalty amount
            - Drip: DRIP (Dividend Reinvestment Plan) flag
            - Reference: Reference information
            - Notes: Additional notes
            - TrustFundAccountRecId: Trust fund account reference
            - RecId: Unique transaction record ID

        Raises:
            APIError: If the API returns an error
            ValidationError: If date format is invalid
        """
        endpoint = f"{self.base_path}/History"
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
