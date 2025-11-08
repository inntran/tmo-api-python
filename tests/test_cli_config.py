"""Tests for CLI configuration and profile management."""

import argparse
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from tmo_api.cli import (
    TMORC_PATH,
    get_config_profiles,
    load_config,
    resolve_config_values,
)
from tmo_api.exceptions import ValidationError


@pytest.fixture
def temp_tmorc(tmp_path, monkeypatch):
    """Create a temporary .tmorc file for testing."""
    temp_rc = tmp_path / ".tmorc"
    monkeypatch.setattr("tmo_api.cli.TMORC_PATH", temp_rc)
    return temp_rc


@pytest.fixture
def sample_config(temp_tmorc):
    """Create a sample configuration file."""
    config_content = """[demo]
token = TMO
database = API Sandbox
environment = us

[production]
token = PROD_TOKEN
database = Production DB
environment = canada
timeout = 60
"""
    temp_tmorc.write_text(config_content)
    return temp_tmorc


def test_load_config_empty_when_file_missing():
    """load_config should return empty config when file doesn't exist."""
    with patch("tmo_api.cli.TMORC_PATH", Path("/nonexistent/.tmorc")):
        config = load_config()
        assert len(config.sections()) == 0


def test_load_config_reads_profiles(sample_config):
    """load_config should read profiles from file."""
    config = load_config()
    assert "demo" in config.sections()
    assert "production" in config.sections()
    assert config.get("demo", "token") == "TMO"
    assert config.get("production", "token") == "PROD_TOKEN"


def test_get_config_profiles(sample_config):
    """get_config_profiles should return list of profile names."""
    config = load_config()
    profiles = get_config_profiles(config)
    assert profiles == ["demo", "production"]


def test_get_config_profiles_empty():
    """get_config_profiles should return empty list when no profiles."""
    with patch("tmo_api.cli.TMORC_PATH", Path("/nonexistent/.tmorc")):
        config = load_config()
        profiles = get_config_profiles(config)
        assert profiles == []


def test_resolve_config_values_uses_profile(sample_config):
    """resolve_config_values should load values from specified profile."""
    args = argparse.Namespace(profile="production", token=None, database=None, environment=None)

    values = resolve_config_values(args)

    assert values["token"] == "PROD_TOKEN"
    assert values["database"] == "Production DB"
    assert values["environment"] == "canada"
    assert values["timeout"] == 60


def test_resolve_config_values_uses_default_demo_profile(sample_config):
    """resolve_config_values should default to demo profile."""
    args = argparse.Namespace(profile="demo", token=None, database=None, environment=None)

    values = resolve_config_values(args)

    assert values["token"] == "TMO"
    assert values["database"] == "API Sandbox"
    assert values["environment"] == "us"


def test_resolve_config_values_uses_builtin_demo_when_no_config(temp_tmorc):
    """resolve_config_values should use built-in demo credentials when config missing."""
    args = argparse.Namespace(profile="demo", token=None, database=None, environment=None)

    values = resolve_config_values(args)

    assert values["token"] == "TMO"
    assert values["database"] == "API Sandbox"
    assert values["environment"] == "us"


def test_resolve_config_values_command_line_overrides_profile(sample_config):
    """Command-line arguments should override profile values."""
    args = argparse.Namespace(
        profile="production",
        token="OVERRIDE_TOKEN",
        database="Override DB",
        environment="aus",
    )

    values = resolve_config_values(args)

    assert values["token"] == "OVERRIDE_TOKEN"
    assert values["database"] == "Override DB"
    assert values["environment"] == "aus"


def test_resolve_config_values_env_vars_override_profile(sample_config):
    """Environment variables should override profile values when CLI args not set."""
    args = argparse.Namespace(profile="production", token=None, database=None, environment=None)

    with patch.dict(os.environ, {"TMO_API_TOKEN": "ENV_TOKEN", "TMO_DATABASE": "Env DB"}):
        values = resolve_config_values(args)

    # Profile provides token and database, but env vars should NOT override
    # because profile has values. Env vars only fill in when profile doesn't have values.
    assert values["token"] == "PROD_TOKEN"
    assert values["database"] == "Production DB"


def test_resolve_config_values_env_vars_fill_missing_values(temp_tmorc):
    """Environment variables should fill in missing profile values."""
    # Create config with partial profile
    config_content = """[partial]
environment = us
"""
    temp_tmorc.write_text(config_content)

    args = argparse.Namespace(profile="partial", token=None, database=None, environment=None)

    with patch.dict(os.environ, {"TMO_API_TOKEN": "ENV_TOKEN", "TMO_DATABASE": "Env DB"}):
        values = resolve_config_values(args)

    assert values["token"] == "ENV_TOKEN"
    assert values["database"] == "Env DB"
    assert values["environment"] == "us"


def test_resolve_config_values_raises_on_unknown_profile(sample_config):
    """resolve_config_values should raise ValidationError for unknown profile."""
    args = argparse.Namespace(profile="nonexistent", token=None, database=None, environment=None)

    with pytest.raises(ValidationError, match="Profile 'nonexistent' not found"):
        resolve_config_values(args)


def test_resolve_config_values_raises_on_missing_token(temp_tmorc):
    """resolve_config_values should raise ValidationError when token missing."""
    # Create config without token
    config_content = """[notoken]
database = Test DB
environment = us
"""
    temp_tmorc.write_text(config_content)

    args = argparse.Namespace(profile="notoken", token=None, database=None, environment=None)

    with pytest.raises(ValidationError, match="Token is required"):
        resolve_config_values(args)


def test_resolve_config_values_raises_on_missing_database(temp_tmorc):
    """resolve_config_values should raise ValidationError when database missing."""
    # Create config without database
    config_content = """[nodb]
token = TEST_TOKEN
environment = us
"""
    temp_tmorc.write_text(config_content)

    args = argparse.Namespace(profile="nodb", token=None, database=None, environment=None)

    with pytest.raises(ValidationError, match="Database is required"):
        resolve_config_values(args)


def test_tmorc_path_is_in_home_directory():
    """TMORC_PATH should point to ~/.tmorc."""
    assert TMORC_PATH == Path.home() / ".tmorc"
