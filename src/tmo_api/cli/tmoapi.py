#!/usr/bin/env python3
"""CLI tool for TMO API documentation and data operations."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import TMORC_PATH

console = Console()


API_DOC_URL = (
    "https://developers.themortgageoffice.com/api/collections/37774064/2sAXjGcE4E"
    "?environment=28403304-b9b941d0-8d12-427d-80c7-46429d5af299&segregateAuth=true&versionTag=latest"
)

METHOD_COLORS = {
    "GET": "rgb(0,127,49)",
    "POST": "rgb(173,122,3)",
    "PATCH": "rgb(98,52,151)",
    "DELETE": "rgb(142,26,16)",
}


def find_assets_dir() -> Path:  # pragma: no cover
    """Find the assets/postman_collection directory.

    Checks in order:
    1. Project root's assets directory (for development) - looks for pyproject.toml
    2. Installed package's assets directory (for production)

    Returns:
        Path to the assets/postman_collection directory (may not exist yet)
    """
    # First, try to find project root by looking for pyproject.toml (development mode)
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent / "assets" / "postman_collection"

    # Fall back to package installation directory (production mode)
    # __file__ is .../tmo_api/cli/tmoapi.py
    # parent.parent is .../tmo_api/
    package_dir = Path(__file__).parent.parent
    return package_dir / "assets" / "postman_collection"


def find_api_spec(api_spec: Optional[str]) -> Path:  # pragma: no cover
    """Find the API documentation file.

    Args:
        api_spec: Optional path to doc file

    Returns:
        Path to the doc file

    Raises:
        SystemExit if file not found
    """
    if api_spec:
        doc_path = Path(api_spec)
    else:
        # Check the assets directory (works for both development and production)
        assets_dir = find_assets_dir()
        if assets_dir.exists():
            candidates = sorted(assets_dir.glob("tmo_api_collection_*.json"), reverse=True)
            if candidates:
                doc_path = candidates[0]
                if doc_path.exists():
                    return doc_path

        # Fall back to current directory
        candidates = sorted(Path(".").glob("tmo_api_collection_*.json"), reverse=True)
        if candidates:
            doc_path = candidates[0]
        else:
            console.print(
                "[red]Error: No API documentation file found.[/red]\n"
                "Use [cyan]tmoapi download[/cyan] first or specify --api-spec"
            )
            sys.exit(1)

    if not doc_path.exists():
        console.print(f"[red]Error: Documentation file {doc_path} not found[/red]")
        sys.exit(1)

    return doc_path


def load_collection(api_spec: Path) -> Dict[str, Any]:  # pragma: no cover
    """Load Postman collection from file.

    Args:
        api_spec: Path to the collection file

    Returns:
        Parsed collection data
    """
    with open(api_spec, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
        return data


def iter_collection_requests(
    items: List[Dict[str, Any]], folder_path: str = ""
) -> Iterator[Dict[str, Any]]:
    """Yield every request item in the collection along with its full path."""
    for item in items:
        if "request" in item:
            name = item.get("name", "Unnamed")
            full_path = f"{folder_path}/{name}" if folder_path else name
            yield {"item": item, "path": full_path}
        elif "item" in item:
            folder_name = item.get("name", "Unnamed Folder")
            new_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
            yield from iter_collection_requests(item["item"], new_path)


def extract_url_from_request(request_info: Dict[str, Any]) -> str:
    """Extract URL from request object.

    Args:
        request_info: Request information from Postman collection

    Returns:
        URL path (without base URL to avoid duplication)
    """
    if isinstance(request_info.get("url"), str):
        url: str = str(request_info["url"])
        # Strip common base URL if present
        if "api.themortgageoffice.com" in url:
            parts = url.split("api.themortgageoffice.com", 1)
            return str(parts[1])
        return url
    elif "urlObject" in request_info:
        url_obj = request_info["urlObject"]
        path = "/".join(url_obj.get("path", []))
        return "/" + path if path else ""
    return ""


def get_method_color(method: str) -> str:  # pragma: no cover
    """Get Rich color for HTTP method.

    Args:
        method: HTTP method name

    Returns:
        Rich color string
    """
    return METHOD_COLORS.get(method, "white")


def html_to_rich(html_text: Any) -> str:
    """Convert HTML to rich console markup.

    Args:
        html_text: Text containing HTML tags (can be str or other types)

    Returns:
        Text with rich console markup
    """
    if not html_text:
        return ""

    # Convert to string if not already
    if not isinstance(html_text, str):
        html_text = str(html_text)

    import re

    text = html_text

    # Convert tables to Rich table format
    # We'll use a placeholder that we can replace later with actual Rich tables
    def simplify_table(match: re.Match[str]) -> str:
        table_html = match.group(0)
        rows: List[List[str]] = []

        # Extract all rows
        row_matches = re.finditer(r"<tr>(.*?)</tr>", table_html, re.DOTALL)
        for row_match in row_matches:
            row_html = row_match.group(1)
            # Extract cells (th or td)
            cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row_html, re.DOTALL)
            if cells:
                # Clean each cell
                clean_cells = []
                for cell in cells:
                    # Remove HTML tags from cell
                    clean_cell = re.sub(r"<[^>]+>", "", cell)
                    clean_cell = clean_cell.strip()
                    clean_cells.append(clean_cell)
                rows.append(clean_cells)

        # Format as text using Rich table-style formatting
        if not rows:
            return ""

        # Use Rich Console to render table
        from io import StringIO

        from rich.box import MARKDOWN

        # Use actual terminal width so table can size columns based on content
        string_io = StringIO()
        temp_console = Console(file=string_io, force_terminal=True, width=console.width)
        rich_table = Table(
            show_header=True, header_style="", box=MARKDOWN, expand=False, show_lines=True
        )

        # Add columns based on first row (headers)
        if rows:
            for header in rows[0]:
                rich_table.add_column(header)

            # Add data rows
            for row in rows[1:]:
                rich_table.add_row(*row)

        # Render table to string
        temp_console.print(rich_table)
        rendered = string_io.getvalue()

        return "\n" + rendered + "\n"

    # Replace tables with simplified version
    text = re.sub(r"<table[^>]*>.*?</table>", simplify_table, text, flags=re.DOTALL)

    # Convert lists to simpler format
    # Ordered lists
    text = re.sub(r"<ol[^>]*>(.*?)</ol>", lambda m: "\n" + m.group(1) + "\n", text, flags=re.DOTALL)
    # Unordered lists
    text = re.sub(r"<ul[^>]*>(.*?)</ul>", lambda m: "\n" + m.group(1) + "\n", text, flags=re.DOTALL)
    # List items - add bullet or number
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"  • \1\n", text, flags=re.DOTALL)

    # Convert headers
    text = re.sub(r"<h[1-6][^>]*>(.*?)</h[1-6]>", r"[bold]\1[/bold]\n", text, flags=re.DOTALL)

    # Convert paragraphs
    text = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", text, flags=re.DOTALL)

    # Simple HTML to rich markup conversion
    text = text.replace("<b>", "[bold]").replace("</b>", "[/bold]")
    text = text.replace("<strong>", "[bold]").replace("</strong>", "[/bold]")
    text = text.replace("<i>", "[italic]").replace("</i>", "[/italic]")
    text = text.replace("<em>", "[italic]").replace("</em>", "[/italic]")
    text = text.replace("<u>", "[underline]").replace("</u>", "[/underline]")
    text = text.replace("<code>", "[cyan]").replace("</code>", "[/cyan]")

    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = text.replace("&nbsp;", " ")

    # Remove excessive whitespace while preserving paragraph breaks
    # Replace multiple newlines with at most 2 newlines (one blank line)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    # Remove spaces at the beginning and end of lines
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)

    return text.strip()


def get_assets_output_path(filename: str) -> Path:  # pragma: no cover
    """Get the output path in assets/postman_collection directory.

    Args:
        filename: The filename to save

    Returns:
        Path to save the file in assets/postman_collection
    """
    assets_dir = find_assets_dir()
    assets_dir.mkdir(parents=True, exist_ok=True)
    return assets_dir / filename


def get_filename_from_data(data: Dict[str, Any]) -> str:
    """Generate filename from API documentation data.

    Args:
        data: The API documentation data

    Returns:
        Filename based on publish date or default name
    """
    publish_date = data.get("info", {}).get("publishDate")
    if publish_date:
        # Parse ISO date and format as YYYYMMDD
        dt = datetime.fromisoformat(publish_date.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y%m%d")
        return f"tmo_api_collection_{date_str}.json"
    else:
        return "tmo_api_collection.json"


def persist_api_document(data: Dict[str, Any], output_override: Optional[str] = None) -> Path:
    """Write API documentation data and return the output path."""
    filename = get_filename_from_data(data)
    output_path = Path(output_override) if output_override else get_assets_output_path(filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output_path


def download_api_doc(args: argparse.Namespace) -> None:  # pragma: no cover
    """Download API documentation and save to file.

    For development use: saves to assets/postman_collection directory.
    End users will consume the pre-downloaded specs from their installation.
    """
    try:
        console.print("[cyan]Downloading API documentation...[/cyan]")
        response = requests.get(API_DOC_URL, timeout=30)
        response.raise_for_status()

        data = response.json()
        output_path = persist_api_document(data, args.output)

        console.print(f"[green]✓[/green] API documentation saved to [bold]{output_path}[/bold]")
        publish_date = data.get("info", {}).get("publishDate")
        if publish_date:
            console.print(f"[dim]Publish date: {publish_date}[/dim]")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error downloading API documentation: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error processing API documentation: {e}[/red]")
        sys.exit(1)


def copy_api_doc(args: argparse.Namespace) -> None:  # pragma: no cover
    """Copy API documentation from a URL or local file and save to assets/postman_collection.

    For development use: copies an old version of API spec from a URL or file path
    and saves it to the assets/postman_collection directory.
    """
    try:
        source = args.source
        console.print(f"[cyan]Loading API documentation from {source}...[/cyan]")

        # Check if source is a local file path
        # Try to resolve as absolute or relative path
        source_path = Path(source).resolve()
        if source_path.exists() and source_path.is_file():
            # Copy from local file
            with open(source_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif source.startswith(("http://", "https://")):
            # Copy from URL
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            data = response.json()
        else:
            # Not a valid file or URL
            console.print(f"[red]Error: '{source}' is not a valid file path or URL[/red]")
            sys.exit(1)

        output_path = persist_api_document(data)

        console.print(
            f"[green]✓[/green] API documentation copied and saved to [bold]{output_path}[/bold]"
        )
        publish_date = data.get("info", {}).get("publishDate")
        if publish_date:
            console.print(f"[dim]Publish date: {publish_date}[/dim]")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error loading API documentation: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error processing API documentation: {e}[/red]")
        sys.exit(1)


def list_endpoints(args: argparse.Namespace) -> None:  # pragma: no cover
    """List all API endpoints with HTTP verbs and URLs."""
    try:
        api_spec = find_api_spec(args.api_spec)
        data = load_collection(api_spec)

        endpoints = []
        for entry in iter_collection_requests(data.get("item", [])):
            request_info = entry["item"]["request"]
            method = request_info.get("method", "GET")
            url = extract_url_from_request(request_info)
            endpoints.append(
                {
                    "name": entry["path"],
                    "method": method,
                    "url": url,
                    "id": entry["item"].get("id", ""),
                }
            )

        # Sort by name
        endpoints.sort(key=lambda x: x["name"])

        # Create a rich table
        table = Table(title=f"TMO API Endpoints ({len(endpoints)} total)")
        table.add_column("Method", style="cyan", width=8)
        table.add_column("Name", style="green")
        table.add_column("URL", style="blue")

        for endpoint in endpoints:
            method_color = get_method_color(endpoint["method"])
            table.add_row(
                f"[{method_color}]{endpoint['method']}[/{method_color}]",
                endpoint["name"],
                endpoint["url"],
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error reading API documentation: {e}[/red]")
        sys.exit(1)


def search_endpoints(items: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """Recursively search for endpoints matching the search term.

    Args:
        items: List of items from Postman collection
        search_term: Search term to match

    Returns:
        List of matching items with metadata
    """
    matches = []
    search_lower = search_term.lower()

    for entry in iter_collection_requests(items):
        item = entry["item"]
        item_name = item.get("name", "")
        item_id = item.get("id", "")
        full_name = entry["path"]
        request_info = item["request"]
        url = extract_url_from_request(request_info)

        # Match by ID, name, path or URL
        if (
            item_id == search_term
            or search_lower in item_name.lower()
            or search_lower in full_name.lower()
            or search_lower in url.lower()
        ):
            matches.append(
                {
                    "item": item,
                    "path": full_name,
                    "url": url,
                    "method": request_info.get("method", "GET"),
                }
            )

    return matches


def show_matches_table(matches: List[Dict[str, Any]], search_term: str) -> None:  # pragma: no cover
    """Display a table of multiple matching endpoints.

    Args:
        matches: List of matching endpoints
        search_term: Original search term
    """
    console.print(
        f"[yellow]Found {len(matches)} matching endpoints. Please be more specific:[/yellow]\n"
    )

    table = Table(title=f"Matching Endpoints for '{search_term}'")
    table.add_column("Method", style="cyan", width=8)
    table.add_column("Name", style="green")
    table.add_column("Path", style="blue")
    table.add_column("ID", style="dim")

    for match in matches:
        method = match["method"]
        method_color = get_method_color(method)
        table.add_row(
            f"[{method_color}]{method}[/{method_color}]",
            match["item"].get("name", "Unnamed"),
            match["path"],
            match["item"].get("id", "N/A"),
        )

    console.print(table)
    console.print("\n[dim]Tip: Use the full path or endpoint ID for an exact match[/dim]")


def show_endpoint(args: argparse.Namespace) -> None:  # pragma: no cover
    """Show documentation for a specific endpoint."""
    try:
        api_spec = find_api_spec(args.api_spec)
        data = load_collection(api_spec)

        # Search for endpoints
        items = data.get("item", [])
        matches = search_endpoints(items, args.endpoint)

        if not matches:
            console.print(f"[red]Error: Endpoint '{args.endpoint}' not found[/red]")
            sys.exit(1)

        # If multiple matches, show list and exit
        if len(matches) > 1:
            show_matches_table(matches, args.endpoint)
            sys.exit(0)

        # Single match - show detailed view
        found_item = matches[0]["item"]
        found_path = matches[0]["path"]

        # Extract endpoint information
        request_info = found_item["request"]
        method = request_info.get("method", "GET")
        method_color = get_method_color(method)
        url = extract_url_from_request(request_info)

        title = f"[bold]{found_item.get('name', 'Unnamed')}[/bold]"
        content = []

        content.append(f"[{method_color}]{method}[/{method_color}] [blue]{url}[/blue]")
        content.append(f"[dim]Path: {found_path}[/dim]")
        content.append(f"[dim]ID: {found_item.get('id', 'N/A')}[/dim]")

        # Display description with HTML converted to rich markup
        description = request_info.get("description", "")
        if description:
            rich_description = html_to_rich(description)
            content.append("")
            content.append("[bold]Description:[/bold]")
            content.append(rich_description)

        # Display headers if any
        headers = request_info.get("header", [])
        if headers:
            content.append("")
            content.append("[bold]Headers:[/bold]")
            for header_info in headers:
                if isinstance(header_info, dict):
                    header_name = header_info.get("key", "")
                    header_value = header_info.get("value", "")
                    header_desc = header_info.get("description", "")
                    if header_desc:
                        if isinstance(header_desc, dict):
                            header_desc = header_desc.get("content", str(header_desc))
                        header_desc = html_to_rich(header_desc)
                        content.append(f"  [cyan]{header_name}[/cyan]: {header_desc}")
                    else:
                        content.append(f"  [cyan]{header_name}[/cyan]: {header_value}")

        # Display URL path variables if any
        if "urlObject" in request_info:
            url_obj = request_info["urlObject"]
            variables = url_obj.get("variable", [])
            if variables:
                content.append("")
                content.append("[bold]Path Variables:[/bold]")
                for var in variables:
                    if isinstance(var, dict):
                        var_name = var.get("key", "")
                        var_value = var.get("value", "")
                        var_desc = var.get("description", "")
                        # Handle description that might be a dict or string
                        if var_desc:
                            if isinstance(var_desc, dict):
                                # Extract content if it's a dict
                                var_desc = var_desc.get("content", str(var_desc))
                            var_desc = html_to_rich(var_desc)
                            content.append(f"  [cyan]:{var_name}[/cyan]: {var_desc}")
                        else:
                            content.append(f"  [cyan]:{var_name}[/cyan]: (default: {var_value})")

        # Display query parameters if any
        if "urlObject" in request_info:
            url_obj = request_info["urlObject"]
            query_params = url_obj.get("query", [])
            if query_params:
                content.append("")
                content.append("[bold]Query Parameters:[/bold]")
                for param in query_params:
                    if isinstance(param, dict):
                        param_name = param.get("key", "")
                        param_value = param.get("value", "")
                        param_desc = param.get("description", "")
                        if param_desc:
                            if isinstance(param_desc, dict):
                                param_desc = param_desc.get("content", str(param_desc))
                            param_desc = html_to_rich(param_desc)
                            content.append(f"  [cyan]{param_name}[/cyan]: {param_desc}")
                        else:
                            content.append(f"  [cyan]{param_name}[/cyan]: {param_value}")

        # Display request body if any
        body = request_info.get("body", {})
        if body:
            body_mode = body.get("mode", "")
            if body_mode:
                content.append("")
                content.append(f"[bold]Request Body ({body_mode}):[/bold]")
                if body_mode == "raw":
                    raw_body = body.get("raw", "")
                    if raw_body and len(raw_body) < 5000:
                        content.append(f"[dim]{raw_body}[/dim]")
                    elif raw_body:
                        content.append(f"[dim]{raw_body[:5000]}...[/dim]")

        panel = Panel("\n".join(content), title=title, border_style="green")
        console.print(panel)

    except Exception as e:
        console.print(f"[red]Error reading endpoint documentation: {e}[/red]")
        sys.exit(1)


def init_config(args: argparse.Namespace) -> None:  # pragma: no cover
    """Initialize or update ~/.tmorc configuration file."""
    console.print("[cyan]Initializing TMO API configuration...[/cyan]\n")

    if TMORC_PATH.exists() and not args.force:
        console.print(f"[yellow]Config file already exists at:[/yellow]")
        console.print(f"  [bold]{TMORC_PATH}[/bold]\n")
        console.print("[dim]Use --force to overwrite the existing file[/dim]")
        sys.exit(1)

    # Create default config with demo profile
    config_content = """# TMO API Configuration File
# Location: ~/.tmorc
# Format: INI-style configuration with profiles

[demo]
token = TMO
database = API Sandbox
environment = us

# Add your custom profiles below
# Example:
# [production]
# token = YOUR_TOKEN_HERE
# database = YOUR_DATABASE_NAME
# environment = us
# timeout = 30
"""

    console.print(f"[cyan]Writing configuration file to:[/cyan]")
    console.print(f"  [bold]{TMORC_PATH}[/bold]\n")

    TMORC_PATH.write_text(config_content)

    console.print(f"[green]✓[/green] Configuration file created successfully!\n")
    console.print("[bold]What's inside:[/bold]")
    console.print("  • Default '[cyan]demo[/cyan]' profile (TMO API Sandbox)")
    console.print("  • Template for adding your own profiles\n")

    console.print("[bold]Next steps:[/bold]")
    console.print("  1. Edit the file to add your production credentials:")
    console.print(f"     [dim]vim {TMORC_PATH}[/dim]")
    console.print("  2. Use profiles in CLI commands:")
    console.print("     [dim]tmopo shares pools              # Uses 'demo' profile[/dim]")
    console.print("     [dim]tmopo -P production shares pools # Uses 'production' profile[/dim]")
    console.print("  3. Override with command-line flags if needed:")
    console.print("     [dim]tmopo --token XXX --database YYY shares pools[/dim]")


def main() -> None:  # pragma: no cover
    """Main entry point for tmoapi command."""
    parser = argparse.ArgumentParser(
        description="TMO API Documentation and Data Tool", prog="tmoapi"
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Init configuration subcommand
    init_parser = subparsers.add_parser("init", help="Initialize ~/.tmorc configuration file")
    init_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing configuration file"
    )

    # Download documentation subcommand
    download_parser = subparsers.add_parser("download", help="Download API documentation")
    download_parser.add_argument(
        "-o", "--output", type=str, help="Output file path (default: auto-generated)"
    )

    # Load documentation subcommand
    copy_parser = subparsers.add_parser("copy", help="Copy API documentation from URL or file")
    copy_parser.add_argument(
        "source", type=str, help="URL or file path to copy API documentation from"
    )

    # List endpoints subcommand
    list_parser = subparsers.add_parser("list", help="List all API endpoints")
    list_parser.add_argument(
        "-f", "--api-spec", type=str, help="API documentation file (default: auto-detect)"
    )

    # Show endpoint subcommand
    show_parser = subparsers.add_parser("show", help="Show documentation for a specific endpoint")
    show_parser.add_argument("endpoint", type=str, help="Endpoint name or ID to show")
    show_parser.add_argument(
        "-f", "--api-spec", type=str, help="API documentation file (default: auto-detect)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "init":
        init_config(args)
    elif args.command == "download":
        download_api_doc(args)
    elif args.command == "copy":
        copy_api_doc(args)
    elif args.command == "list":
        list_endpoints(args)
    elif args.command == "show":
        show_endpoint(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
