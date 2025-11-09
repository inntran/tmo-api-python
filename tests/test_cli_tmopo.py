"""Tests for the tmopo CLI helpers."""

from argparse import Namespace
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from tmo_api.cli import tmopo
from tmo_api.cli.tmopo import execute_shares_action, validate_shares_args
from tmo_api.exceptions import AuthenticationError, ValidationError


def make_args(**overrides):
    """Helper to build argparse.Namespace instances."""
    defaults = {
        "shares_action": "pools",
        "pool": None,
        "id": None,
        "recid": None,
        "partner": None,
        "start_date": "01/01/2024",
        "end_date": "01/31/2024",
        "output": None,
    }
    defaults.update(overrides)
    return Namespace(**defaults)


def test_validate_shares_args_requires_pool_for_pool_actions():
    args = make_args(shares_action="pools-get")
    with pytest.raises(ValidationError):
        validate_shares_args(args)


def test_validate_shares_args_assigns_pool_from_positional_id():
    args = make_args(shares_action="pools-get", id="POOL123")

    validate_shares_args(args)

    assert args.pool == "POOL123"


def test_validate_shares_args_assigns_record_id():
    args = make_args(shares_action="distributions-get", id="REC999")

    validate_shares_args(args)

    assert args.recid == "REC999"


def test_validate_shares_args_assigns_partner():
    args = make_args(shares_action="partners-get", id="PARTNER-1")

    validate_shares_args(args)

    assert args.partner == "PARTNER-1"


def build_client() -> SimpleNamespace:
    """Create a dummy client with resource placeholders."""
    return SimpleNamespace(
        shares_pools=SimpleNamespace(),
        shares_partners=SimpleNamespace(),
        shares_distributions=SimpleNamespace(),
        shares_certificates=SimpleNamespace(),
        shares_history=SimpleNamespace(),
    )


@pytest.mark.parametrize(
    "action,resource_attr,method_name,args_kwargs,expected_call",
    [
        ("pools", "shares_pools", "list_all", {}, ()),
        (
            "pools-bank-accounts",
            "shares_pools",
            "get_pool_bank_accounts",
            {"pool": "POOL1"},
            ("POOL1",),
        ),
        (
            "partners",
            "shares_partners",
            "list_all",
            {"start_date": "01/01/2024", "end_date": "01/31/2024"},
            ("01/01/2024", "01/31/2024"),
        ),
        (
            "distributions",
            "shares_distributions",
            "list_all",
            {"start_date": "01/01/2024", "end_date": "01/31/2024", "pool": "POOL1"},
            ("01/01/2024", "01/31/2024", "POOL1"),
        ),
        (
            "certificates",
            "shares_certificates",
            "get_certificates",
            {
                "start_date": "01/01/2024",
                "end_date": "01/31/2024",
                "partner": "PARTNER-1",
                "pool": "POOL1",
            },
            ("01/01/2024", "01/31/2024", "PARTNER-1", "POOL1"),
        ),
        (
            "history",
            "shares_history",
            "get_history",
            {
                "start_date": "01/01/2024",
                "end_date": "01/31/2024",
                "partner": "PARTNER-1",
                "pool": "POOL1",
            },
            ("01/01/2024", "01/31/2024", "PARTNER-1", "POOL1"),
        ),
    ],
)
def test_execute_shares_action_dispatch(
    action, resource_attr, method_name, args_kwargs, expected_call
):
    client = build_client()
    resource = getattr(client, resource_attr)
    method = MagicMock(return_value="payload")
    setattr(resource, method_name, method)

    args = make_args(shares_action=action, **args_kwargs)

    result = execute_shares_action(client, args)

    assert result == "payload"
    method.assert_called_once_with(*expected_call)


def test_execute_shares_action_unknown_action():
    client = build_client()
    args = make_args(shares_action="unknown")

    with pytest.raises(ValidationError):
        execute_shares_action(client, args)


def test_shares_command_suggests_expanded_range(monkeypatch, capsys):
    args = make_args(shares_action="partners", start_date=None, end_date=None)

    def fake_apply_defaults(local_args):
        local_args._used_default_dates = True
        local_args.start_date = "02/01/2024"
        local_args.end_date = "03/01/2024"

    monkeypatch.setattr(tmopo, "apply_default_date_ranges", fake_apply_defaults)
    monkeypatch.setattr(tmopo, "validate_shares_args", lambda _: None)
    monkeypatch.setattr(tmopo, "create_client_from_args", lambda _: object())
    monkeypatch.setattr(tmopo, "execute_shares_action", lambda *_, **__: [])

    def fail_handle_output(*_args, **_kwargs):
        raise AssertionError("handle_output should not be used for empty default results")

    monkeypatch.setattr(tmopo, "handle_output", fail_handle_output)

    tmopo.shares_command(args)

    captured = capsys.readouterr()
    assert "No results found in the last 31 days." in captured.out
    assert "tmopo shares partners --start-date" in captured.out


def test_shares_command_prints_formatted_output(monkeypatch, capsys):
    args = make_args()

    monkeypatch.setattr(tmopo, "validate_shares_args", lambda _: None)
    monkeypatch.setattr(tmopo, "create_client_from_args", lambda _: object())
    monkeypatch.setattr(tmopo, "execute_shares_action", lambda *_: [{"id": 1}])

    # handle_output prints directly, so we mock it to print a test string
    def mock_handle_output(result, output_path):
        # When output_path is None, it prints text to stdout
        if output_path is None:
            print(f"text:{len(result)}")

    monkeypatch.setattr(tmopo, "handle_output", mock_handle_output)

    tmopo.shares_command(args)

    captured = capsys.readouterr()
    assert captured.out.strip() == "text:1"


def test_shares_command_handles_authentication_error(monkeypatch, capsys):
    args = make_args()

    monkeypatch.setattr(tmopo, "validate_shares_args", lambda _: None)
    monkeypatch.setattr(tmopo, "create_client_from_args", lambda _: object())

    def raise_auth_error(*_args, **_kwargs):
        raise AuthenticationError("bad credentials")

    monkeypatch.setattr(tmopo, "execute_shares_action", raise_auth_error)

    with pytest.raises(SystemExit) as exit_info:
        tmopo.shares_command(args)

    assert exit_info.value.code == 1
    captured = capsys.readouterr()
    assert "Authentication Error" in captured.err
    assert "Check your token and database credentials" in captured.err


def test_capital_command_exits_with_placeholder_message(capsys):
    args = Namespace()

    with pytest.raises(SystemExit) as exit_info:
        tmopo.capital_command(args)

    assert exit_info.value.code == 1
    captured = capsys.readouterr()
    assert "tmopo capital: TMO Capital Pools CLI" in captured.err
    assert "placeholder" in captured.err
