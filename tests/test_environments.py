"""Tests for environment configurations."""

import pytest

from tmo_api.environments import DEFAULT_ENVIRONMENT, Environment


class TestEnvironments:
    """Test environment configurations."""

    def test_us_environment(self):
        """Test US environment URL."""
        assert Environment.US.value == "https://api.themortgageoffice.com"

    def test_canada_environment(self):
        """Test Canada environment URL."""
        assert Environment.CANADA.value == "https://api-ca.themortgageoffice.com"

    def test_australia_environment(self):
        """Test Australia environment URL."""
        assert Environment.AUSTRALIA.value == "https://api-aus.themortgageoffice.com"

    def test_default_environment(self):
        """Test default environment is US."""
        assert DEFAULT_ENVIRONMENT == Environment.US

    def test_environment_enum_members(self):
        """Test all expected environment members exist."""
        expected_members = {"US", "CANADA", "AUSTRALIA"}
        actual_members = {env.name for env in Environment}
        assert expected_members == actual_members

    def test_environment_values_are_https(self):
        """Test all environment URLs use HTTPS."""
        for env in Environment:
            assert env.value.startswith("https://")
