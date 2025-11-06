"""Tests for PoolsResource."""

from unittest.mock import Mock, patch

import pytest

from tmo_api.client import TMOClient
from tmo_api.exceptions import ValidationError
from tmo_api.models.pool import Pool
from tmo_api.resources.pools import PoolsResource, PoolType


class TestPoolsResource:
    """Test PoolsResource functionality."""

    @pytest.fixture
    def client(self, mock_token, mock_database):
        """Create a test client."""
        return TMOClient(token=mock_token, database=mock_database)

    def test_pools_resource_init_shares(self, client):
        """Test PoolsResource initialization with Shares type."""
        resource = PoolsResource(client, PoolType.SHARES)
        assert resource.client == client
        assert resource.pool_type == PoolType.SHARES
        assert resource.base_path == "LSS.svc/Shares"

    def test_pools_resource_init_capital(self, client):
        """Test PoolsResource initialization with Capital type."""
        resource = PoolsResource(client, PoolType.CAPITAL)
        assert resource.pool_type == PoolType.CAPITAL
        assert resource.base_path == "LSS.svc/Capital"

    @patch.object(TMOClient, "get")
    def test_get_pool_success(self, mock_get, client, mock_pool_account, mock_api_response_success):
        """Test successful get_pool call."""
        mock_get.return_value = mock_api_response_success
        resource = PoolsResource(client, PoolType.SHARES)

        pool = resource.get_pool(mock_pool_account)

        mock_get.assert_called_once_with(f"LSS.svc/Shares/Pools/{mock_pool_account}")
        assert pool is not None
        assert isinstance(pool, Pool)

    @patch.object(TMOClient, "get")
    def test_get_pool_empty_account(self, mock_get, client):
        """Test get_pool with empty account raises ValidationError."""
        resource = PoolsResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.get_pool("")

        assert "Account parameter is required" in str(exc_info.value)
        mock_get.assert_not_called()

    @patch.object(TMOClient, "get")
    def test_get_pool_partners(self, mock_get, client, mock_pool_account):
        """Test get_pool_partners."""
        mock_get.return_value = {"Status": 0, "Data": [{"partner_id": 1}]}
        resource = PoolsResource(client, PoolType.SHARES)

        partners = resource.get_pool_partners(mock_pool_account)

        mock_get.assert_called_once_with(f"LSS.svc/Shares/Pools/{mock_pool_account}/Partners")
        assert isinstance(partners, list)

    @patch.object(TMOClient, "get")
    def test_get_pool_loans(self, mock_get, client, mock_pool_account):
        """Test get_pool_loans."""
        mock_get.return_value = {"Status": 0, "Data": [{"loan_id": 1}]}
        resource = PoolsResource(client, PoolType.SHARES)

        loans = resource.get_pool_loans(mock_pool_account)

        mock_get.assert_called_once_with(f"LSS.svc/Shares/Pools/{mock_pool_account}/Loans")
        assert isinstance(loans, list)

    @patch.object(TMOClient, "get")
    def test_get_pool_bank_accounts(self, mock_get, client, mock_pool_account):
        """Test get_pool_bank_accounts."""
        mock_get.return_value = {"Status": 0, "Data": [{"account_id": 1}]}
        resource = PoolsResource(client, PoolType.SHARES)

        accounts = resource.get_pool_bank_accounts(mock_pool_account)

        mock_get.assert_called_once_with(f"LSS.svc/Shares/Pools/{mock_pool_account}/BankAccounts")
        assert isinstance(accounts, list)

    @patch.object(TMOClient, "get")
    def test_get_pool_attachments(self, mock_get, client, mock_pool_account):
        """Test get_pool_attachments."""
        mock_get.return_value = {"Status": 0, "Data": [{"attachment_id": 1}]}
        resource = PoolsResource(client, PoolType.SHARES)

        attachments = resource.get_pool_attachments(mock_pool_account)

        mock_get.assert_called_once_with(f"LSS.svc/Shares/Pools/{mock_pool_account}/Attachments")
        assert isinstance(attachments, list)

    @patch.object(TMOClient, "get")
    def test_list_all_pools(self, mock_get, client, mock_pools_response):
        """Test list_all pools."""
        mock_get.return_value = mock_pools_response
        resource = PoolsResource(client, PoolType.SHARES)

        pools = resource.list_all()

        mock_get.assert_called_once_with("LSS.svc/Shares/Pools")
        assert isinstance(pools, list)
        assert all(isinstance(pool, Pool) for pool in pools)

    def test_pool_type_enum(self):
        """Test PoolType enum values."""
        assert PoolType.SHARES.value == "Shares"
        assert PoolType.CAPITAL.value == "Capital"
