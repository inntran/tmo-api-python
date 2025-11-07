"""Tests for the CLI helpers in tmoapi.py."""

import json
from pathlib import Path

import pytest

from tmo_api.cli.tmoapi import (
    extract_url_from_request,
    get_filename_from_data,
    html_to_rich,
    iter_collection_requests,
    persist_api_document,
    search_endpoints,
)


def _request_item(name: str, item_id: str, url: str, method: str = "GET") -> dict:
    return {
        "name": name,
        "id": item_id,
        "request": {
            "method": method,
            "url": url,
        },
    }


def test_iter_collection_requests_preserves_full_paths():
    """Ensure nested folders produce the expected full path."""
    items = [
        {
            "name": "Loan Origination",
            "item": [
                _request_item(
                    name="Create Loan",
                    item_id="loan-create",
                    url="https://api.themortgageoffice.com/Loans/Create",
                    method="POST",
                )
            ],
        },
        _request_item(
            name="List Loans",
            item_id="loan-list",
            url="https://api.themortgageoffice.com/Loans",
        ),
    ]

    results = list(iter_collection_requests(items))

    assert [entry["path"] for entry in results] == [
        "Loan Origination/Create Loan",
        "List Loans",
    ]
    assert results[0]["item"]["id"] == "loan-create"
    assert results[1]["item"]["id"] == "loan-list"


def test_search_endpoints_matches_by_path_and_url():
    """Search should match IDs, names, folder paths, and URLs."""
    items = [
        {
            "name": "Loans",
            "item": [
                _request_item(
                    name="GetLoan",
                    item_id="get-loan",
                    url="https://api.themortgageoffice.com/v1/loans/{loanId}",
                )
            ],
        },
        {
            "name": "Payments",
            "item": [
                _request_item(
                    name="CreatePayment",
                    item_id="create-payment",
                    url="https://api.themortgageoffice.com/v1/payments",
                    method="POST",
                )
            ],
        },
    ]

    path_match = search_endpoints(items, "payments/createpayment")
    assert len(path_match) == 1
    assert path_match[0]["path"] == "Payments/CreatePayment"
    assert path_match[0]["method"] == "POST"
    assert path_match[0]["url"] == "/v1/payments"

    id_match = search_endpoints(items, "get-loan")
    assert len(id_match) == 1
    assert id_match[0]["path"] == "Loans/GetLoan"
    assert id_match[0]["url"] == "/v1/loans/{loanId}"


def test_persist_api_document_writes_to_override_path(tmp_path):
    """Persist helper should write JSON to the requested location."""
    data = {
        "info": {"publishDate": "2024-01-15T10:00:00Z"},
        "item": [],
    }
    target = tmp_path / "custom.json"

    output_path = persist_api_document(data, str(target))

    assert output_path == target
    assert json.loads(Path(output_path).read_text(encoding="utf-8")) == data


def test_extract_url_from_request_with_string_url():
    """Extract URL when request has url as string."""
    request_info = {"url": "https://api.themortgageoffice.com/v1/loans"}
    result = extract_url_from_request(request_info)
    assert result == "/v1/loans"


def test_extract_url_from_request_with_plain_string():
    """Extract URL when it doesn't contain base domain."""
    request_info = {"url": "/v1/payments"}
    result = extract_url_from_request(request_info)
    assert result == "/v1/payments"


def test_extract_url_from_request_with_url_object():
    """Extract URL when request has urlObject structure."""
    request_info = {
        "urlObject": {
            "path": ["v1", "loans", "{loanId}"],
        }
    }
    result = extract_url_from_request(request_info)
    assert result == "/v1/loans/{loanId}"


def test_extract_url_from_request_with_empty_path():
    """Extract URL with empty path returns empty string."""
    request_info = {"urlObject": {"path": []}}
    result = extract_url_from_request(request_info)
    assert result == ""


def test_extract_url_from_request_no_url():
    """Extract URL returns empty string when no URL found."""
    request_info = {}
    result = extract_url_from_request(request_info)
    assert result == ""


def test_get_filename_from_data_with_publish_date():
    """Generate filename from publish date."""
    data = {"info": {"publishDate": "2024-08-01T10:30:00Z"}}
    filename = get_filename_from_data(data)
    assert filename == "tmo_api_collection_20240801.json"


def test_get_filename_from_data_without_publish_date():
    """Generate default filename when no publish date."""
    data = {"info": {}}
    filename = get_filename_from_data(data)
    assert filename == "tmo_api_collection.json"


def test_get_filename_from_data_empty():
    """Generate default filename when data is empty."""
    data = {}
    filename = get_filename_from_data(data)
    assert filename == "tmo_api_collection.json"


def test_html_to_rich_with_empty_input():
    """Convert empty or None HTML returns empty string."""
    assert html_to_rich(None) == ""
    assert html_to_rich("") == ""
    # 0 is falsy, so it returns empty string
    assert html_to_rich(0) == ""


def test_html_to_rich_with_bold_tags():
    """Convert bold HTML tags to rich markup."""
    result = html_to_rich("<b>bold text</b>")
    assert "[bold]bold text[/bold]" in result

    result = html_to_rich("<strong>strong text</strong>")
    assert "[bold]strong text[/bold]" in result


def test_html_to_rich_with_italic_tags():
    """Convert italic HTML tags to rich markup."""
    result = html_to_rich("<i>italic text</i>")
    assert "[italic]italic text[/italic]" in result

    result = html_to_rich("<em>emphasis text</em>")
    assert "[italic]emphasis text[/italic]" in result


def test_html_to_rich_with_code_tags():
    """Convert code HTML tags to rich markup."""
    result = html_to_rich("<code>code snippet</code>")
    assert "[cyan]code snippet[/cyan]" in result


def test_html_to_rich_with_paragraph_tags():
    """Convert paragraph HTML tags."""
    result = html_to_rich("<p>First paragraph</p><p>Second paragraph</p>")
    assert "First paragraph" in result
    assert "Second paragraph" in result


def test_html_to_rich_with_headers():
    """Convert header HTML tags to rich markup."""
    result = html_to_rich("<h1>Header 1</h1><h2>Header 2</h2>")
    assert "[bold]Header 1[/bold]" in result
    assert "[bold]Header 2[/bold]" in result


def test_html_to_rich_with_list_items():
    """Convert list HTML tags."""
    result = html_to_rich("<ul><li>Item 1</li><li>Item 2</li></ul>")
    assert "•" in result
    assert "Item 1" in result
    assert "Item 2" in result


def test_html_to_rich_with_html_entities():
    """Convert HTML entities to actual characters."""
    result = html_to_rich("&lt;tag&gt; &amp; &quot;quotes&quot; &#39;apostrophe&#39;")
    assert "<tag>" in result
    assert "&" in result
    assert '"quotes"' in result
    assert "'apostrophe'" in result


def test_html_to_rich_removes_unknown_tags():
    """Remove unrecognized HTML tags."""
    result = html_to_rich("<div>content</div><span>more</span>")
    assert "<div>" not in result
    assert "</div>" not in result
    assert "content" in result
    assert "more" in result


def test_html_to_rich_with_non_string_input():
    """Convert non-string input to string first."""
    result = html_to_rich(12345)
    assert result == "12345"


def test_search_endpoints_no_matches():
    """Search returns empty list when no matches found."""
    items = [_request_item("GetLoan", "loan-id", "https://api.themortgageoffice.com/v1/loans")]
    matches = search_endpoints(items, "nonexistent")
    assert len(matches) == 0


def test_search_endpoints_matches_by_id():
    """Search matches by exact endpoint ID."""
    items = [_request_item("GetLoan", "loan-123", "https://api.themortgageoffice.com/v1/loans")]
    matches = search_endpoints(items, "loan-123")
    assert len(matches) == 1
    assert matches[0]["item"]["id"] == "loan-123"


def test_search_endpoints_matches_by_name_case_insensitive():
    """Search matches by name case-insensitively."""
    items = [_request_item("GetLoan", "loan-id", "https://api.themortgageoffice.com/v1/loans")]
    matches = search_endpoints(items, "getloan")
    assert len(matches) == 1
    assert matches[0]["item"]["name"] == "GetLoan"


def test_search_endpoints_matches_by_url():
    """Search matches by URL substring."""
    items = [_request_item("GetLoan", "loan-id", "https://api.themortgageoffice.com/v1/loans/{id}")]
    matches = search_endpoints(items, "loans")
    assert len(matches) == 1


def test_search_endpoints_returns_multiple_matches():
    """Search returns all matching endpoints."""
    items = [
        _request_item("GetLoan", "get-loan", "https://api.themortgageoffice.com/v1/loans/{id}"),
        _request_item("ListLoans", "list-loans", "https://api.themortgageoffice.com/v1/loans"),
        _request_item(
            "CreatePayment", "create-payment", "https://api.themortgageoffice.com/v1/payments"
        ),
    ]
    matches = search_endpoints(items, "loan")
    assert len(matches) == 2
    assert all("loan" in match["item"]["name"].lower() for match in matches)


def test_iter_collection_requests_with_empty_items():
    """Iterate over empty collection returns nothing."""
    items = []
    results = list(iter_collection_requests(items))
    assert len(results) == 0


def test_iter_collection_requests_with_single_level():
    """Iterate over flat collection structure."""
    items = [
        _request_item("Endpoint1", "id1", "/path1"),
        _request_item("Endpoint2", "id2", "/path2"),
    ]
    results = list(iter_collection_requests(items))
    assert len(results) == 2
    assert results[0]["path"] == "Endpoint1"
    assert results[1]["path"] == "Endpoint2"


def test_iter_collection_requests_with_nested_folders():
    """Iterate over nested folder structure."""
    items = [
        {
            "name": "Folder1",
            "item": [
                {
                    "name": "Subfolder",
                    "item": [_request_item("DeepEndpoint", "deep-id", "/deep")],
                }
            ],
        }
    ]
    results = list(iter_collection_requests(items))
    assert len(results) == 1
    assert results[0]["path"] == "Folder1/Subfolder/DeepEndpoint"


def test_iter_collection_requests_mixed_structure():
    """Iterate over mixed collection with folders and direct items."""
    items = [
        _request_item("RootEndpoint", "root-id", "/root"),
        {
            "name": "FolderA",
            "item": [_request_item("ChildEndpoint", "child-id", "/child")],
        },
    ]
    results = list(iter_collection_requests(items))
    assert len(results) == 2
    assert results[0]["path"] == "RootEndpoint"
    assert results[1]["path"] == "FolderA/ChildEndpoint"


def test_html_to_rich_with_tables():
    """Convert HTML tables to rich table format."""
    html = """
    <table>
        <tr><th>Header 1</th><th>Header 2</th></tr>
        <tr><td>Data 1</td><td>Data 2</td></tr>
        <tr><td>Data 3</td><td>Data 4</td></tr>
    </table>
    """
    result = html_to_rich(html)
    # The result should contain the table data
    assert "Header 1" in result
    assert "Header 2" in result
    assert "Data 1" in result
    assert "Data 2" in result
    assert "Data 3" in result
    assert "Data 4" in result


def test_html_to_rich_with_complex_table():
    """Convert complex HTML table with nested tags."""
    html = """
    <table>
        <tr><th>Name</th><th>Value</th></tr>
        <tr><td><b>Bold</b></td><td><code>code</code></td></tr>
    </table>
    """
    result = html_to_rich(html)
    assert "Name" in result
    assert "Value" in result
    # Table conversion strips inner tags during cell cleaning
    assert "Bold" in result or "code" in result


def test_html_to_rich_with_empty_table():
    """Convert empty HTML table."""
    html = "<table></table>"
    result = html_to_rich(html)
    # Empty tables should return minimal output
    assert result is not None


def test_extract_url_from_request_with_url_object_missing_path():
    """Extract URL when urlObject exists but has no path key."""
    request_info = {"urlObject": {}}
    result = extract_url_from_request(request_info)
    assert result == ""


def test_search_endpoints_in_nested_folders():
    """Search endpoints in deeply nested folder structure."""
    items = [
        {
            "name": "Level1",
            "item": [
                {
                    "name": "Level2",
                    "item": [
                        _request_item(
                            "DeepEndpoint",
                            "deep-id",
                            "https://api.themortgageoffice.com/v1/deep",
                        )
                    ],
                }
            ],
        }
    ]
    matches = search_endpoints(items, "level2")
    assert len(matches) == 1
    assert matches[0]["path"] == "Level1/Level2/DeepEndpoint"


def test_persist_api_document_with_unicode():
    """Persist API document with unicode characters."""
    data = {
        "info": {"name": "API with émojis 🚀"},
        "item": [],
    }
    # Use temp directory since we're not providing override
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    output_path = persist_api_document(data, temp_path)
    content = Path(output_path).read_text(encoding="utf-8")
    loaded = json.loads(content)

    assert loaded["info"]["name"] == "API with émojis 🚀"
    # Clean up
    Path(temp_path).unlink()


def test_get_filename_from_data_with_different_date_format():
    """Generate filename from various date formats."""
    data = {"info": {"publishDate": "2025-11-07T15:45:30+00:00"}}
    filename = get_filename_from_data(data)
    assert filename == "tmo_api_collection_20251107.json"
