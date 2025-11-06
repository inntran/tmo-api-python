"""Tests for PartnersResource."""

from unittest.mock import patch

import pytest

from tmo_api.client import TMOClient
from tmo_api.exceptions import ValidationError
from tmo_api.resources.partners import PartnersResource
from tmo_api.resources.pools import PoolType


class TestPartnersResource:
    """Test PartnersResource functionality."""

    @pytest.fixture
    def client(self, mock_token, mock_database):
        """Create a test client."""
        return TMOClient(token=mock_token, database=mock_database)

    def test_partners_resource_init_shares(self, client):
        """Test PartnersResource initialization with Shares type."""
        resource = PartnersResource(client, PoolType.SHARES)
        assert resource.client == client
        assert resource.pool_type == PoolType.SHARES
        assert resource.base_path == "LSS.svc/Shares"

    def test_partners_resource_init_capital(self, client):
        """Test PartnersResource initialization with Capital type."""
        resource = PartnersResource(client, PoolType.CAPITAL)
        assert resource.pool_type == PoolType.CAPITAL
        assert resource.base_path == "LSS.svc/Capital"

    @patch.object(TMOClient, "get")
    def test_get_partner_success(self, mock_get, client, mock_api_response_success):
        """Test successful get_partner call."""
        mock_get.return_value = mock_api_response_success
        resource = PartnersResource(client, PoolType.SHARES)

        partner = resource.get_partner("PARTNER001")

        mock_get.assert_called_once_with("LSS.svc/Shares/Partners/PARTNER001")
        assert partner is not None

    @patch.object(TMOClient, "get")
    def test_get_partner_empty_account(self, mock_get, client):
        """Test get_partner with empty account raises ValidationError."""
        resource = PartnersResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.get_partner("")

        assert "Account parameter is required" in str(exc_info.value)
        mock_get.assert_not_called()

    @patch.object(TMOClient, "get")
    def test_get_partner_attachments(self, mock_get, client):
        """Test get_partner_attachments."""
        mock_get.return_value = {"Status": 0, "Data": [{"attachment_id": 1}]}
        resource = PartnersResource(client, PoolType.SHARES)

        attachments = resource.get_partner_attachments("PARTNER001")

        mock_get.assert_called_once_with("LSS.svc/Shares/Partners/PARTNER001/Attachments")
        assert isinstance(attachments, list)

    @patch.object(TMOClient, "get")
    def test_get_partner_attachments_empty_account(self, mock_get, client):
        """Test get_partner_attachments with empty account raises ValidationError."""
        resource = PartnersResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.get_partner_attachments("")

        assert "Account parameter is required" in str(exc_info.value)
        mock_get.assert_not_called()

    @patch.object(TMOClient, "get")
    def test_list_all_no_filters(self, mock_get, client):
        """Test list_all without filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"partner_id": 1}]}
        resource = PartnersResource(client, PoolType.SHARES)

        partners = resource.list_all()

        mock_get.assert_called_once_with("LSS.svc/Shares/Partners", params=None)
        assert isinstance(partners, list)

    @patch.object(TMOClient, "get")
    def test_list_all_with_date_filters(self, mock_get, client):
        """Test list_all with date filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"partner_id": 1}]}
        resource = PartnersResource(client, PoolType.SHARES)

        partners = resource.list_all(start_date="01/01/2024", end_date="12/31/2024")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/Partners",
            params={"from-date": "01/01/2024", "to-date": "12/31/2024"},
        )
        assert isinstance(partners, list)

    @patch.object(TMOClient, "get")
    def test_list_all_invalid_start_date(self, mock_get, client):
        """Test list_all with invalid start_date format."""
        resource = PartnersResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.list_all(start_date="2024-01-01")

        assert "start_date must be in MM/DD/YYYY format" in str(exc_info.value)
        mock_get.assert_not_called()

    @patch.object(TMOClient, "get")
    def test_list_all_invalid_end_date(self, mock_get, client):
        """Test list_all with invalid end_date format."""
        resource = PartnersResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.list_all(end_date="invalid-date")

        assert "end_date must be in MM/DD/YYYY format" in str(exc_info.value)
        mock_get.assert_not_called()

    def test_validate_date_format_valid(self, client):
        """Test _validate_date_format with valid date."""
        resource = PartnersResource(client, PoolType.SHARES)

        assert resource._validate_date_format("12/31/2024") is True
        assert resource._validate_date_format("01/01/2024") is True

    def test_validate_date_format_invalid(self, client):
        """Test _validate_date_format with invalid dates."""
        resource = PartnersResource(client, PoolType.SHARES)

        assert resource._validate_date_format("2024-12-31") is False
        assert resource._validate_date_format("31/12/2024") is False
        assert resource._validate_date_format("invalid") is False
