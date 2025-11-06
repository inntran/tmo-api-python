"""Tests for Pool models."""

from datetime import datetime

import pytest

from tmo_api.models.pool import OtherAsset, OtherLiability, Pool, PoolResponse, PoolsResponse


class TestOtherAsset:
    """Test OtherAsset model."""

    def test_other_asset_initialization(self):
        """Test OtherAsset initialization."""
        data = {
            "rec_id": 123,
            "Description": "Test Asset",
            "Value": 10000.00,
            "DateLastEvaluated": "12/31/2024",
        }
        asset = OtherAsset(data)

        assert asset.rec_id == 123
        assert asset.Description == "Test Asset"
        assert asset.Value == 10000.00
        assert isinstance(asset.DateLastEvaluated, datetime)
        assert asset.DateLastEvaluated == datetime(2024, 12, 31)

    def test_other_asset_without_date(self):
        """Test OtherAsset without date."""
        data = {"rec_id": 456, "Description": "Asset without date"}
        asset = OtherAsset(data)

        assert asset.rec_id == 456
        assert asset.Description == "Asset without date"


class TestOtherLiability:
    """Test OtherLiability model."""

    def test_other_liability_initialization(self):
        """Test OtherLiability initialization."""
        data = {
            "rec_id": 789,
            "Description": "Test Liability",
            "Balance": 50000.00,
            "MaturityDate": "06/30/2025",
            "PaymentNextDue": "01/15/2025",
        }
        liability = OtherLiability(data)

        assert liability.rec_id == 789
        assert liability.Description == "Test Liability"
        assert liability.Balance == 50000.00
        assert isinstance(liability.MaturityDate, datetime)
        assert liability.MaturityDate == datetime(2025, 6, 30)
        assert isinstance(liability.PaymentNextDue, datetime)
        assert liability.PaymentNextDue == datetime(2025, 1, 15)

    def test_other_liability_without_dates(self):
        """Test OtherLiability without dates."""
        data = {"rec_id": 101, "Description": "Liability without dates"}
        liability = OtherLiability(data)

        assert liability.rec_id == 101
        assert liability.Description == "Liability without dates"


class TestPool:
    """Test Pool model."""

    def test_pool_initialization(self):
        """Test Pool initialization with basic data."""
        data = {
            "rec_id": 1,
            "Account": "POOL001",
            "Name": "Test Pool",
            "InceptionDate": "01/01/2024",
            "LastEvaluation": "12/31/2024",
            "SysTimeStamp": "11/15/2024",
        }
        pool = Pool(data)

        assert pool.rec_id == 1
        assert pool.Account == "POOL001"
        assert pool.Name == "Test Pool"
        assert isinstance(pool.InceptionDate, datetime)
        assert pool.InceptionDate == datetime(2024, 1, 1)
        assert isinstance(pool.LastEvaluation, datetime)
        assert pool.LastEvaluation == datetime(2024, 12, 31)
        assert isinstance(pool.SysTimeStamp, datetime)
        assert pool.SysTimeStamp == datetime(2024, 11, 15)

    def test_pool_with_nested_objects(self):
        """Test Pool with nested OtherAssets and OtherLiabilities."""
        data = {
            "rec_id": 2,
            "Account": "POOL002",
            "OtherAssets": [
                {"rec_id": 10, "Description": "Asset 1", "Value": 1000},
                {"rec_id": 11, "Description": "Asset 2", "Value": 2000},
            ],
            "OtherLiabilities": [
                {"rec_id": 20, "Description": "Liability 1", "Balance": 5000},
            ],
        }
        pool = Pool(data)

        assert pool.rec_id == 2
        assert len(pool.OtherAssets) == 2
        assert isinstance(pool.OtherAssets[0], OtherAsset)
        assert pool.OtherAssets[0].Description == "Asset 1"
        assert pool.OtherAssets[1].Description == "Asset 2"

        assert len(pool.OtherLiabilities) == 1
        assert isinstance(pool.OtherLiabilities[0], OtherLiability)
        assert pool.OtherLiabilities[0].Description == "Liability 1"

    def test_pool_repr(self):
        """Test Pool string representation."""
        data = {"rec_id": 999, "Account": "POOL999"}
        pool = Pool(data)
        assert repr(pool) == "Pool(999)"


class TestPoolResponse:
    """Test PoolResponse model."""

    def test_pool_response_with_data(self):
        """Test PoolResponse with pool data."""
        response_data = {
            "Status": 0,
            "Data": {
                "rec_id": 1,
                "Account": "POOL001",
                "Name": "Test Pool",
            },
        }
        response = PoolResponse(response_data)

        assert response.status == 0
        assert response.pool is not None
        assert isinstance(response.pool, Pool)
        assert response.pool.Account == "POOL001"

    def test_pool_response_without_data(self):
        """Test PoolResponse without pool data."""
        response_data = {"Status": 1, "ErrorMessage": "Not found", "ErrorNumber": 404}
        response = PoolResponse(response_data)

        assert response.status == 1
        assert response.pool is None
        assert response.error_message == "Not found"

    def test_pool_response_repr(self):
        """Test PoolResponse string representation."""
        response_data = {"Status": 0, "Data": {"rec_id": 1}}
        response = PoolResponse(response_data)
        assert repr(response) == "PoolResponse(status=0)"


class TestPoolsResponse:
    """Test PoolsResponse model."""

    def test_pools_response_with_list(self):
        """Test PoolsResponse with list of pools."""
        response_data = {
            "Status": 0,
            "Data": [
                {"rec_id": 1, "Account": "POOL001"},
                {"rec_id": 2, "Account": "POOL002"},
                {"rec_id": 3, "Account": "POOL003"},
            ],
        }
        response = PoolsResponse(response_data)

        assert response.status == 0
        assert len(response.pools) == 3
        assert all(isinstance(pool, Pool) for pool in response.pools)
        assert response.pools[0].Account == "POOL001"
        assert response.pools[1].Account == "POOL002"
        assert response.pools[2].Account == "POOL003"

    def test_pools_response_with_single_pool(self):
        """Test PoolsResponse with single pool dict."""
        response_data = {"Status": 0, "Data": {"rec_id": 1, "Account": "POOL001"}}
        response = PoolsResponse(response_data)

        assert response.status == 0
        assert len(response.pools) == 1
        assert isinstance(response.pools[0], Pool)
        assert response.pools[0].Account == "POOL001"

    def test_pools_response_empty(self):
        """Test PoolsResponse with empty data."""
        response_data = {"Status": 0, "Data": []}
        response = PoolsResponse(response_data)

        assert response.status == 0
        assert len(response.pools) == 0

    def test_pools_response_repr(self):
        """Test PoolsResponse string representation."""
        response_data = {"Status": 0, "Data": []}
        response = PoolsResponse(response_data)
        assert repr(response) == "PoolsResponse(status=0)"
