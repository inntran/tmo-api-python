"""Tests for DistributionsResource."""

from unittest.mock import patch

import pytest

from tmo_api.client import TMOClient
from tmo_api.exceptions import ValidationError
from tmo_api.resources.distributions import DistributionsResource
from tmo_api.resources.pools import PoolType


class TestDistributionsResource:
    """Test DistributionsResource functionality."""

    @pytest.fixture
    def client(self, mock_token, mock_database):
        """Create a test client."""
        return TMOClient(token=mock_token, database=mock_database)

    def test_distributions_resource_init_shares(self, client):
        """Test DistributionsResource initialization with Shares type."""
        resource = DistributionsResource(client, PoolType.SHARES)
        assert resource.client == client
        assert resource.pool_type == PoolType.SHARES
        assert resource.base_path == "LSS.svc/Shares"

    def test_distributions_resource_init_capital(self, client):
        """Test DistributionsResource initialization with Capital type."""
        resource = DistributionsResource(client, PoolType.CAPITAL)
        assert resource.pool_type == PoolType.CAPITAL
        assert resource.base_path == "LSS.svc/Capital"

    @patch.object(TMOClient, "get")
    def test_get_distribution_success(self, mock_get, client, mock_api_response_success):
        """Test successful get_distribution call."""
        mock_get.return_value = mock_api_response_success
        resource = DistributionsResource(client, PoolType.SHARES)

        distribution = resource.get_distribution("12345")

        mock_get.assert_called_once_with("LSS.svc/Shares/Distributions/12345")
        assert distribution is not None

    @patch.object(TMOClient, "get")
    def test_get_distribution_empty_rec_id(self, mock_get, client):
        """Test get_distribution with empty rec_id raises ValidationError."""
        resource = DistributionsResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.get_distribution("")

        assert "RecID parameter is required" in str(exc_info.value)
        mock_get.assert_not_called()

    @patch.object(TMOClient, "get")
    def test_list_all_no_filters(self, mock_get, client):
        """Test list_all without filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"distribution_id": 1}]}
        resource = DistributionsResource(client, PoolType.SHARES)

        distributions = resource.list_all()

        mock_get.assert_called_once_with("LSS.svc/Shares/Distributions", params=None)
        assert isinstance(distributions, list)

    @patch.object(TMOClient, "get")
    def test_list_all_with_date_filters(self, mock_get, client):
        """Test list_all with date filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"distribution_id": 1}]}
        resource = DistributionsResource(client, PoolType.SHARES)

        distributions = resource.list_all(start_date="01/01/2024", end_date="12/31/2024")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/Distributions",
            params={"from-date": "01/01/2024", "to-date": "12/31/2024"},
        )
        assert isinstance(distributions, list)

    @patch.object(TMOClient, "get")
    def test_list_all_with_pool_account(self, mock_get, client):
        """Test list_all with pool_account filter."""
        mock_get.return_value = {"Status": 0, "Data": [{"distribution_id": 1}]}
        resource = DistributionsResource(client, PoolType.SHARES)

        distributions = resource.list_all(pool_account="POOL001")

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/Distributions", params={"pool-account": "POOL001"}
        )
        assert isinstance(distributions, list)

    @patch.object(TMOClient, "get")
    def test_list_all_with_all_filters(self, mock_get, client):
        """Test list_all with all filters."""
        mock_get.return_value = {"Status": 0, "Data": [{"distribution_id": 1}]}
        resource = DistributionsResource(client, PoolType.SHARES)

        distributions = resource.list_all(
            start_date="01/01/2024", end_date="12/31/2024", pool_account="POOL001"
        )

        mock_get.assert_called_once_with(
            "LSS.svc/Shares/Distributions",
            params={
                "from-date": "01/01/2024",
                "to-date": "12/31/2024",
                "pool-account": "POOL001",
            },
        )
        assert isinstance(distributions, list)

    @patch.object(TMOClient, "get")
    def test_list_all_invalid_start_date(self, mock_get, client):
        """Test list_all with invalid start_date format."""
        resource = DistributionsResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.list_all(start_date="2024-01-01")

        assert "start_date must be in MM/DD/YYYY format" in str(exc_info.value)
        mock_get.assert_not_called()

    @patch.object(TMOClient, "get")
    def test_list_all_invalid_end_date(self, mock_get, client):
        """Test list_all with invalid end_date format."""
        resource = DistributionsResource(client, PoolType.SHARES)

        with pytest.raises(ValidationError) as exc_info:
            resource.list_all(end_date="invalid-date")

        assert "end_date must be in MM/DD/YYYY format" in str(exc_info.value)
        mock_get.assert_not_called()

    def test_validate_date_format_valid(self, client):
        """Test _validate_date_format with valid date."""
        resource = DistributionsResource(client, PoolType.SHARES)

        assert resource._validate_date_format("12/31/2024") is True
        assert resource._validate_date_format("01/01/2024") is True

    def test_validate_date_format_invalid(self, client):
        """Test _validate_date_format with invalid dates."""
        resource = DistributionsResource(client, PoolType.SHARES)

        assert resource._validate_date_format("2024-12-31") is False
        assert resource._validate_date_format("31/12/2024") is False
        assert resource._validate_date_format("invalid") is False
