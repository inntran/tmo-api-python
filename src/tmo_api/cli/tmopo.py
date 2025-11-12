#!/usr/bin/env python3
"""CLI tool for TMO Mortgage Pools API."""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Any

from ..exceptions import APIError, AuthenticationError, NetworkError, TMOException, ValidationError
from . import (
    add_common_arguments,
    apply_default_date_ranges,
    create_client_from_args,
    handle_output,
)


def validate_shares_args(args: argparse.Namespace) -> None:
    """Validate shares subcommand arguments.

    Args:
        args: Parsed command-line arguments

    Raises:
        ValidationError: If required arguments are missing
    """
    action = args.shares_action

    # Actions that require pool parameter
    pool_required_actions = [
        "pools-get",
        "pools-partners",
        "pools-loans",
        "pools-bank-accounts",
        "pools-attachments",
    ]

    # Actions that require record ID parameter
    recid_required_actions = ["distributions-get"]

    # Actions that require partner parameter
    partner_required_actions = ["partners-get", "partners-attachments"]

    # For pool actions, use positional ID or --pool flag
    if action in pool_required_actions:
        if not getattr(args, "pool", None) and not getattr(args, "id", None):
            raise ValidationError(
                f"Action '{action}' requires pool ID (provide as positional argument or use --pool)"
            )
        if not getattr(args, "pool", None) and getattr(args, "id", None):
            args.pool = args.id

    # For record ID actions, use positional ID or --recid flag
    if action in recid_required_actions:
        if not getattr(args, "recid", None) and not getattr(args, "id", None):
            raise ValidationError(  # pragma: no cover - requires integration coverage
                f"Action '{action}' requires record ID (provide as positional argument or use --recid)"
            )
        if not getattr(args, "recid", None) and getattr(args, "id", None):
            args.recid = args.id

    # For partner actions, use positional ID or --partner flag
    if action in partner_required_actions:
        if not getattr(args, "partner", None) and not getattr(args, "id", None):
            raise ValidationError(  # pragma: no cover - requires integration coverage
                f"Action '{action}' requires partner account (provide as positional argument or use --partner)"
            )
        if not getattr(args, "partner", None) and getattr(args, "id", None):
            args.partner = args.id


def execute_shares_action(client, args) -> Any:
    """Execute the specified shares action.

    Args:
        client: TMOClient instance
        args: Parsed command-line arguments

    Returns:
        Action result data

    Raises:
        ValidationError: If action is unknown
    """
    action = args.shares_action

    # Use shares-specific resources
    pools_resource = client.shares_pools
    partners_resource = client.shares_partners
    distributions_resource = client.shares_distributions
    certificates_resource = client.shares_certificates
    history_resource = client.shares_history

    # Pools operations
    if action == "pools":
        return pools_resource.list_all()
    elif action == "pools-get":  # pragma: no cover - exercised via integration tests
        return pools_resource.get_pool(args.pool)
    elif action == "pools-partners":  # pragma: no cover - exercised via integration tests
        # Returns: List of partners with complete financial and contact information
        # Financial: BegCapital, Contributions, Distributions, EndCapital, Income, Withdrawals,
        #            WithdrawalsAndDisbursements, IRR (Internal Rate of Return)
        # Contact: Account, SortName, Address, Phone, Email, TIN
        # Flags: ERISA, IsACH, AccountType
        # Object type: CPartners:#TmoAPI
        return pools_resource.get_pool_partners(args.pool)
    elif action == "pools-loans":  # pragma: no cover - exercised via integration tests
        return pools_resource.get_pool_loans(args.pool)
    elif action == "pools-bank-accounts":
        return pools_resource.get_pool_bank_accounts(args.pool)
    elif action == "pools-attachments":  # pragma: no cover - exercised via integration tests
        return pools_resource.get_pool_attachments(args.pool)

    # Partners operations
    elif action == "partners":
        # Requires: Date range (start_date, end_date) for filtering by DateCreated/LastChanged
        # Returns: List of partners with contact info, CustomFields, trustee info (TrusteeName, TrusteeAccountRef)
        # Contains: Account, Name, Address, Phone, Email, TIN, ERISA flag, IsACH flag, DateCreated, LastChanged
        # Object type: CPSSPartners:#TmoAPI
        return partners_resource.list_all(args.start_date, args.end_date)
    elif action == "partners-get":  # pragma: no cover - exercised via integration tests
        # Returns: Single exact matching partner entry
        # Contains: Contact info (name, address, phone, email), ACH details, CustomFields,
        #           trustee info (TrusteeRecID, TrusteeAccountRef), tax info (TIN), delivery options
        # Does NOT include: Financial transactions like Contributions/Distributions (use pools-partners for that)
        # Object type: CPartner:#TmoAPI
        return partners_resource.get_partner(args.partner)
    elif action == "partners-attachments":  # pragma: no cover - exercised via integration tests
        return partners_resource.get_partner_attachments(args.partner)

    # Distributions operations
    elif action == "distributions":
        return distributions_resource.list_all(args.start_date, args.end_date, args.pool)
    elif action == "distributions-get":  # pragma: no cover - exercised via integration tests
        return distributions_resource.get_distribution(args.recid)

    # Certificates operations (shares only)
    elif action == "certificates":
        return certificates_resource.get_certificates(
            args.start_date, args.end_date, args.partner, args.pool
        )

    # History operations
    elif action == "history":
        # Returns: List of share transaction history records
        # Contains: Transaction details (Amount, Shares, SharesBalance), dates (DateReceived, DateDeposited),
        #           partner/pool info (PartnerAccount, PartnerRecId, PoolAccount, PoolRecId),
        #           payment details (PayAccount, PayName, PayAddress), certificate info,
        #           ACH details, withholding, penalties, IRR
        # Object type: CTransaction:#TmoAPI.Pss
        return history_resource.get_history(args.start_date, args.end_date, args.partner, args.pool)

    else:
        raise ValidationError(f"Unknown action: {action}")


def shares_command(args: argparse.Namespace) -> None:
    """Handle the shares subcommand.

    Args:
        args: Parsed command-line arguments
    """
    try:
        # Apply default date ranges for actions that support date filtering
        if args.shares_action in ["partners", "distributions", "history", "certificates"]:
            apply_default_date_ranges(args)

        # Validate action-specific arguments
        validate_shares_args(args)

        # Create client
        client = create_client_from_args(args)

        # Execute action
        result = execute_shares_action(client, args)

        # Check if result is empty and we used default dates
        if (
            args.shares_action in ["partners", "distributions", "history", "certificates"]
            and not result
            and hasattr(args, "_used_default_dates")
        ):
            # Suggest expanding the date range
            one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%m/%d/%Y")
            today = datetime.now().strftime("%m/%d/%Y")

            suggested_command = f"tmopo shares {args.shares_action}"
            if args.shares_action == "distributions" and getattr(
                args, "pool", None
            ):  # pragma: no cover
                suggested_command += f" --pool {args.pool}"
            suggested_command += f" --start-date {one_year_ago} --end-date {today}"

            print("No results found in the last 31 days.")
            print(f"Try expanding the date range with:\n{suggested_command}")
            return

        # Handle output (text to stdout, or write to file based on extension)
        output_path = getattr(args, "output", None)
        handle_output(result, output_path)

    except ValidationError as e:  # pragma: no cover - surfaced during manual runs
        print(f"Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except AuthenticationError as e:  # pragma: no cover - surfaced during manual runs
        print(f"Authentication Error: {e}", file=sys.stderr)
        print("Check your token and database credentials", file=sys.stderr)
        sys.exit(1)
    except APIError as e:  # pragma: no cover - surfaced during manual runs
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except NetworkError as e:  # pragma: no cover - surfaced during manual runs
        print(f"Network Error: {e}", file=sys.stderr)
        sys.exit(1)
    except TMOException as e:  # pragma: no cover - surfaced during manual runs
        print(f"SDK Error: {e}", file=sys.stderr)
        sys.exit(1)


def capital_command(args: argparse.Namespace) -> None:  # pragma: no cover - placeholder CLI
    """Handle the capital subcommand (placeholder)."""
    print("tmopo capital: TMO Capital Pools CLI", file=sys.stderr)
    print("This is a placeholder for the Capital pools functionality.", file=sys.stderr)
    print("Usage: tmopo capital [options]", file=sys.stderr)
    sys.exit(1)


def main() -> None:  # pragma: no cover - exercised via CLI entry point
    """Main entry point for tmopo command."""
    # Load config to show available profiles in help
    from . import get_config_profiles, load_config

    config = load_config()
    available_profiles = get_config_profiles(config)
    profiles_text = (
        f"Available profiles: ({', '.join(available_profiles)})"
        if available_profiles
        else "No profiles found (run 'tmoapi init' to create ~/.tmorc)"
    )

    parser = argparse.ArgumentParser(
        description="CLI client for The Mortgage Office API - Mortgage Pools",
        prog="tmopo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Subcommands:
  shares               Manage shares pools (pools, partners, distributions, certificates, history)
  capital              Manage capital pools (placeholder)

Use '%(prog)s <subcommand> --help' for detailed help on each subcommand.

Configuration:
  Default profile is 'demo' (uses TMO API Sandbox)
  Create ~/.tmorc with: tmoapi init
  {profiles_text}
""",
    )

    # Add common arguments
    add_common_arguments(parser)

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Shares subcommand
    shares_parser = subparsers.add_parser(
        "shares",
        help="Manage shares pools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Actions:
  pools                List all shares pools
  pools-get            Get detailed information for a specific shares pool (requires pool account ID)
  pools-partners       List partners for a specific shares pool (requires pool account ID)
  pools-loans          List loans for a specific shares pool (requires pool account ID)
  pools-bank-accounts  List bank accounts for a specific shares pool (requires pool account ID)
  pools-attachments    List attachments for a specific shares pool (requires pool account ID)
  partners             List all shares partners (supports date filtering)
  partners-get         Get detailed information for a specific shares partner (requires partner account)
  partners-attachments List attachments for a specific shares partner (requires partner account)
  distributions        List all shares distributions (supports date and pool filtering)
  distributions-get    Get detailed information for a specific shares distribution (requires distribution record ID)
  certificates         List share certificates (supports date, partner, and pool filtering)
  history              List shares transaction history (supports date, partner, and pool filtering)

Examples:
  # List all shares pools
  tmopo shares pools

  # Get specific pool details (multiple ways)
  tmopo shares pools-get LENDER-C
  tmopo shares pools-get --pool LENDER-C

  # List partners with date filtering
  tmopo shares partners
  tmopo shares partners --start-date 01/01/2024 --end-date 12/31/2024

  # Get partner details
  tmopo shares partners-get P001002
  tmopo shares partners-get --partner P001002

  # List distributions
  tmopo shares distributions
  tmopo shares distributions --pool LENDER-C

  # Get distribution details
  tmopo shares distributions-get 4ABBA93E18D945CF8BC835E7512C8B8F
  tmopo shares distributions-get --recid 4ABBA93E18D945CF8BC835E7512C8B8F

  # Get certificates with filtering
  tmopo shares certificates --start-date 01/01/2024 --end-date 12/31/2024
  tmopo shares certificates --partner P001001 --pool LENDER-C

  # Get transaction history
  tmopo shares history --start-date 01/01/2024 --end-date 12/31/2024
  tmopo shares history --partner P001001

  # Export to different formats
  tmopo shares pools -O pools.json             # JSON format
  tmopo shares pools -O pools.csv              # CSV format (flattened)
  tmopo shares pools -O pools.xlsx             # Excel format (flattened)
  tmopo shares partners -O partners.csv --start-date 01/01/2024
        """,
    )

    shares_parser.add_argument(
        "shares_action",
        help="Action to perform",
        choices=[
            "pools",
            "pools-get",
            "pools-partners",
            "pools-loans",
            "pools-bank-accounts",
            "pools-attachments",
            "partners",
            "partners-get",
            "partners-attachments",
            "distributions",
            "distributions-get",
            "certificates",
            "history",
        ],
    )

    # Optional ID parameter (positional)
    shares_parser.add_argument("id", nargs="?", help="ID parameter for get operations")

    # Explicit ID parameters
    shares_parser.add_argument("--pool", help="Pool account ID")
    shares_parser.add_argument("--recid", help="Record ID (for distribution operations)")
    shares_parser.add_argument("--partner", help="Partner account")

    # Date filtering options
    shares_parser.add_argument("--start-date", help="Start date (MM/DD/YYYY)")
    shares_parser.add_argument("--end-date", help="End date (MM/DD/YYYY)")

    # Output option
    shares_parser.add_argument(
        "-O",
        "--output",
        type=str,
        help="Output file path (format auto-detected from extension: .json, .csv, .xlsx). Defaults to text output to stdout.",
    )

    # Capital subcommand (placeholder)
    capital_parser = subparsers.add_parser("capital", help="Manage capital pools (placeholder)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "shares":
        shares_command(args)
    elif args.command == "capital":
        capital_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
