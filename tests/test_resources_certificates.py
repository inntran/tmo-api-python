"""Tests for CertificatesResource."""

from unittest.mock import patch

import pytest

from tmo_api.client import TMOClient
from tmo_api.exceptions import ValidationError
from tmo_api.resources.certificates import CertificatesResource
from tmo_api.resources.pools import PoolType


class TestCertificatesResource:
    """Test CertificatesResource functionality."""

    @pytest.fixture
    def client(self, mock_token, mock_database):
        """Create a test client."""
        return TMOClient(token=mock_token, database=mock_database)

    def test_certificates_resource_init_shares(self, client):
        """Test CertificatesResource initialization with Shares type."""
        resource = CertificatesResource(client, PoolType.SHARES)
        assert resource.client == client
        assert resource.pool_type == PoolType.SHARES
        assert resource.base_path == "LSS.svc/Shares"

    def test_certificates_resource_init_capital(self, client):
        """Test CertificatesResource initialization with Capital type."""
        resource = CertificatesResource(client, PoolType.CAPITAL)
        assert resource.pool_type == PoolType.CAPITAL
        assert resource.base_path == "LSS.svc/Capital"

    @patch.object(TMOClient, "get")
    def test_get_certificates_no_filters(self, mock_get, client):
        """Test get_certificates without filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"certificate_id": 1}]}
        resource = CertificatesResource(client, PoolType.SHARES)

        certificates = resource.get_certificates()

        mock_get.assert_called_once_with("LSS.svc/Shares/Certificates", params=None)
        assert isinstance(certificates, list)

    @patch.object(TMOClient, "get")
    def test_get_certificates_with_date_filters(self, mock_get, client):
        """Test get_certificates with date filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"certificate_id": 1}]}
        resource = CertificatesResource(client, PoolType.SHARES)

        certificates = resource.get_certificates(start_date="01/01/2024", end_date="12/31/2024")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/Certificates",
            params={"from-date": "01/01/2024", "to-date": "12/31/2024"},
        )
        assert isinstance(certificates, list)

    @patch.object(TMOClient, "get")
    def test_get_certificates_with_partner_account(self, mock_get, client):
        """Test get_certificates with partner_account filter."""
        mock_get.return_value = {"Status": 0, "Data": [{"certificate_id": 1}]}
        resource = CertificatesResource(client, PoolType.SHARES)

        certificates = resource.get_certificates(partner_account="PARTNER001")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/Certificates", params={"partner-account": "PARTNER001"}
        )
        assert isinstance(certificates, list)

    @patch.object(TMOClient, "get")
    def test_get_certificates_with_pool_account(self, mock_get, client):
        """Test get_certificates with pool_account filter."""
        mock_get.return_value = {"Status": 0, "Data": [{"certificate_id": 1}]}
        resource = CertificatesResource(client, PoolType.SHARES)

        certificates = resource.get_certificates(pool_account="POOL001")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/Certificates", params={"pool-account": "POOL001"}
        )
        assert isinstance(certificates, list)

    @patch.object(TMOClient, "get")
    def test_get_certificates_with_all_filters(self, mock_get, client):
        """Test get_certificates with all filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"certificate_id": 1}]}
        resource = CertificatesResource(client, PoolType.SHARES)

        certificates = resource.get_certificates(
            start_date="01/01/2024",
            end_date="12/31/2024",
            partner_account="PARTNER001",
            pool_account="POOL001",
        )

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/Certificates",
            params={
                "from-date": "01/01/2024",
                "to-date": "12/31/2024",
                "partner-account": "PARTNER001",
                "pool-account": "POOL001",
            },
        )
        assert isinstance(certificates, list)

    @patch.object(TMOClient, "get")
    def test_get_certificates_invalid_start_date(self, mock_get, client):
        """Test get_certificates with invalid start_date format."""
        resource = CertificatesResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.get_certificates(start_date="2024-01-01")

        assert "start_date must be in MM/DD/YYYY format" in str(exc_info.value)
        mock_get.assert_not_called()

    @patch.object(TMOClient, "get")
    def test_get_certificates_invalid_end_date(self, mock_get, client):
        """Test get_certificates with invalid end_date format."""
        resource = CertificatesResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.get_certificates(end_date="invalid-date")

        assert "end_date must be in MM/DD/YYYY format" in str(exc_info.value)
        mock_get.assert_not_called()

    def test_validate_date_format_valid(self, client):
        """Test _validate_date_format with valid date."""
        resource = CertificatesResource(client, PoolType.SHARES)

        assert resource._validate_date_format("12/31/2024") is True
        assert resource._validate_date_format("01/01/2024") is True

    def test_validate_date_format_invalid(self, client):
        """Test _validate_date_format with invalid dates."""
        resource = CertificatesResource(client, PoolType.SHARES)

        assert resource._validate_date_format("2024-12-31") is False
        assert resource._validate_date_format("31/12/2024") is False
        assert resource._validate_date_format("invalid") is False
