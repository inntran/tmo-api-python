"""Tests for data models."""

from datetime import datetime

import pytest

from tmo_api.models import BaseModel, BaseResponse


class TestBaseResponse:
    """Test BaseResponse model."""

    def test_base_response_success(self, mock_api_response_success):
        """Test BaseResponse with successful response."""
        response = BaseResponse(mock_api_response_success)
        assert response.status == 0
        assert response.error_message is None
        assert response.error_number is None
        assert response.data == mock_api_response_success["Data"]
        assert response.raw_data == mock_api_response_success

    def test_base_response_error(self, mock_api_response_error):
        """Test BaseResponse with error response."""
        response = BaseResponse(mock_api_response_error)
        assert response.status == 1
        assert response.error_message == "Test error message"
        assert response.error_number == 500
        assert response.data == {}

    def test_base_response_repr(self, mock_api_response_success):
        """Test BaseResponse string representation."""
        response = BaseResponse(mock_api_response_success)
        assert repr(response) == "BaseResponse(status=0)"


class TestBaseModel:
    """Test BaseModel."""

    def test_base_model_initialization(self):
        """Test BaseModel initialization with data."""
        data = {"rec_id": 123, "account": "TEST001", "name": "Test"}
        model = BaseModel(data)
        assert model.rec_id == 123
        assert model.account == "TEST001"
        assert model.name == "Test"
        assert model.raw_data == data

    def test_base_model_repr(self):
        """Test BaseModel string representation."""
        data = {"rec_id": 456}
        model = BaseModel(data)
        assert repr(model) == "BaseModel(456)"

    def test_base_model_repr_without_rec_id(self):
        """Test BaseModel repr without rec_id."""
        data = {"account": "TEST001"}
        model = BaseModel(data)
        assert repr(model) == "BaseModel(unknown)"

    def test_to_snake_case(self):
        """Test CamelCase to snake_case conversion."""
        model = BaseModel({})
        assert model._to_snake_case("CamelCase") == "camel_case"
        assert model._to_snake_case("HTTPResponse") == "h_t_t_p_response"
        assert model._to_snake_case("ID") == "i_d"
        assert model._to_snake_case("lowercase") == "lowercase"

    def test_parse_date_valid_formats(self):
        """Test date parsing with valid formats."""
        model = BaseModel({})

        # Test various date formats
        assert model._parse_date("12/31/2023") == datetime(2023, 12, 31)
        assert model._parse_date("12/31/2023 14:30:00") == datetime(2023, 12, 31, 14, 30, 0)
        assert model._parse_date("2023-12-31T14:30:00") == datetime(2023, 12, 31, 14, 30, 0)
        assert model._parse_date("2023-12-31 14:30:00") == datetime(2023, 12, 31, 14, 30, 0)
        assert model._parse_date("2023-12-31") == datetime(2023, 12, 31)

    def test_parse_date_invalid(self):
        """Test date parsing with invalid format."""
        model = BaseModel({})
        assert model._parse_date("invalid-date") is None
        assert model._parse_date(None) is None
        assert model._parse_date("") is None
