"""Tests for HistoryResource."""

from unittest.mock import patch

import pytest

from tmo_api.client import TMOClient
from tmo_api.exceptions import ValidationError
from tmo_api.resources.history import HistoryResource
from tmo_api.resources.pools import PoolType


class TestHistoryResource:
    """Test HistoryResource functionality."""

    @pytest.fixture
    def client(self, mock_token, mock_database):
        """Create a test client."""
        return TMOClient(token=mock_token, database=mock_database)

    def test_history_resource_init_shares(self, client):
        """Test HistoryResource initialization with Shares type."""
        resource = HistoryResource(client, PoolType.SHARES)
        assert resource.client == client
        assert resource.pool_type == PoolType.SHARES
        assert resource.base_path == "LSS.svc/Shares"

    def test_history_resource_init_capital(self, client):
        """Test HistoryResource initialization with Capital type."""
        resource = HistoryResource(client, PoolType.CAPITAL)
        assert resource.pool_type == PoolType.CAPITAL
        assert resource.base_path == "LSS.svc/Capital"

    @patch.object(TMOClient, "get")
    def test_get_history_no_filters(self, mock_get, client):
        """Test get_history without filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"history_id": 1}]}
        resource = HistoryResource(client, PoolType.SHARES)

        history = resource.get_history()

        mock_get.assert_called_once_with("LSS.svc/Shares/History", params=None)
        assert isinstance(history, list)

    @patch.object(TMOClient, "get")
    def test_get_history_with_date_filters(self, mock_get, client):
        """Test get_history with date filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"history_id": 1}]}
        resource = HistoryResource(client, PoolType.SHARES)

        history = resource.get_history(start_date="01/01/2024", end_date="12/31/2024")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/History",
            params={"from-date": "01/01/2024", "to-date": "12/31/2024"},
        )
        assert isinstance(history, list)

    @patch.object(TMOClient, "get")
    def test_get_history_with_partner_account(self, mock_get, client):
        """Test get_history with partner_account filter."""
        mock_get.return_value = {"Status": 0, "Data": [{"history_id": 1}]}
        resource = HistoryResource(client, PoolType.SHARES)

        history = resource.get_history(partner_account="PARTNER001")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/History", params={"partner-account": "PARTNER001"}
        )
        assert isinstance(history, list)

    @patch.object(TMOClient, "get")
    def test_get_history_with_pool_account(self, mock_get, client):
        """Test get_history with pool_account filter."""
        mock_get.return_value = {"Status": 0, "Data": [{"history_id": 1}]}
        resource = HistoryResource(client, PoolType.SHARES)

        history = resource.get_history(pool_account="POOL001")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/History", params={"pool-account": "POOL001"}
        )
        assert isinstance(history, list)

    @patch.object(TMOClient, "get")
    def test_get_history_with_all_filters(self, mock_get, client):
        """Test get_history with all filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"history_id": 1}]}
        resource = HistoryResource(client, PoolType.SHARES)

        history = resource.get_history(
            start_date="01/01/2024",
            end_date="12/31/2024",
            partner_account="PARTNER001",
            pool_account="POOL001",
        )

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/History",
            params={
                "from-date": "01/01/2024",
                "to-date": "12/31/2024",
                "partner-account": "PARTNER001",
                "pool-account": "POOL001",
            },
        )
        assert isinstance(history, list)

    @patch.object(TMOClient, "get")
    def test_get_history_shares_response_schema(self, mock_get, client):
        """Test Shares history response includes new fields and excludes removed fields."""
        shares_transaction = {
            "__type": "CTransaction:#TmoAPI.Pss",
            "ACH_BatchNumber": "",
            "ACH_TraceNumber": "",
            "ACH_TransNumber": "",
            "Amount": 8003.48,
            "Certificate": "",
            "CertificateRecID": "",
            "Code": "PartnershipReceipt",
            "CreatedBy": "Ramiro",
            "DateCreated": "08/24/2020 11:00:49 AM",
            "DateDeposited": "07/15/2020",
            "DateReceived": "07/15/2020",
            "Description": "Loan Payments-ACH",
            "DistributionRecID": "",
            "Drip": False,
            "LastChanged": "08/24/2020 11:00:49 AM",
            "Notes": "Payment posted from loan servicing.",
            "PartnerAccount": "",
            "PartnerRecId": "",
            "PayAccount": "",
            "PayAddress": "2847 Gundry Avenue",
            "PayName": "World Mortgage Company",
            "Penalty": 0.0,
            "PoolAccount": "LENDER-C",
            "PoolRecId": "dd26c54c785e4eda82065b096c833422",
            "RecId": "D3E01515B6A946E7A2BD1CB4261DF20E",
            "Reference": "0000020",
            "ReversalRecID": "",
            "ShareCost": 0.0,
            "SharePrice": 0.0,
            "Shares": 0.0,
            "SharesBalance": 4207942.53,
            "TDSGroupRecID": "",
            "TransferRecID": "",
            "TrustFundAccountRecId": "5EB27FB365D84699B8343AD43D7A66B4",
            "Withholding": 0.0,
        }
        mock_get.return_value = {"Status": 0, "Data": [shares_transaction]}
        resource = HistoryResource(client, PoolType.SHARES)

        history = resource.get_history()

        assert len(history) == 1
        txn = history[0]
        assert txn["__type"] == "CTransaction:#TmoAPI.Pss"
        # Fields added in Dec 2025 spec
        assert "CertificateRecID" in txn
        assert "DistributionRecID" in txn
        assert "PoolAccount" in txn
        assert "PoolRecId" in txn
        assert "RecId" in txn
        assert "ReversalRecID" in txn
        assert "TDSGroupRecID" in txn
        assert "TransferRecID" in txn
        # Fields removed in Dec 2025 spec
        assert "Date" not in txn
        assert "LenderHistoryRecId" not in txn
        # Dates are human-readable strings, not .NET ticks
        assert not txn["DateCreated"].startswith("/Date(")
        assert not txn["DateReceived"].startswith("/Date(")

    @patch.object(TMOClient, "get")
    def test_get_history_invalid_start_date(self, mock_get, client):
        """Test get_history with invalid start_date format."""
        resource = HistoryResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.get_history(start_date="2024-01-01")

        assert "start_date must be in MM/DD/YYYY format" in str(exc_info.value)
        mock_get.assert_not_called()

    @patch.object(TMOClient, "get")
    def test_get_history_invalid_end_date(self, mock_get, client):
        """Test get_history with invalid end_date format."""
        resource = HistoryResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.get_history(end_date="invalid-date")

        assert "end_date must be in MM/DD/YYYY format" in str(exc_info.value)
        mock_get.assert_not_called()

    def test_validate_date_format_valid(self, client):
        """Test _validate_date_format with valid date."""
        resource = HistoryResource(client, PoolType.SHARES)

        assert resource._validate_date_format("12/31/2024") is True
        assert resource._validate_date_format("01/01/2024") is True

    def test_validate_date_format_invalid(self, client):
        """Test _validate_date_format with invalid dates."""
        resource = HistoryResource(client, PoolType.SHARES)

        assert resource._validate_date_format("2024-12-31") is False
        assert resource._validate_date_format("31/12/2024") is False
        assert resource._validate_date_format("invalid") is False
