# CLI Tools

The SDK ships with multiple CLI tools for working with The Mortgage Office API:

- **`tmoapi`** - API documentation and configuration management
- **`tmopo`** - Mortgage pools operations (shares and capital)
- **`tmols`** - Loan servicing operations (placeholder)
- **`tmolo`** - Loan origination operations (placeholder)

All CLI tools install automatically alongside the library (`pip install tmo-api`).

## Configuration

All TMO CLI tools use a shared configuration file at `~/.tmorc` for storing API credentials and profiles.

### Initialize Configuration

Create the configuration file:

```bash
tmoapi init
```

This creates `~/.tmorc` with a default `demo` profile that connects to the TMO API Sandbox.

### Configuration File Format

The `~/.tmorc` file uses INI format with named profiles:

```ini
[demo]
token = TMO
database = API Sandbox
environment = us

[production]
token = YOUR_TOKEN_HERE
database = YOUR_DATABASE_NAME
environment = us
timeout = 30
```

### Using Profiles

All CLI commands default to the `demo` profile. Use `-P` or `--profile` to select a different profile:

```bash
# Uses demo profile (default)
tmopo shares pools

# Use production profile
tmopo -P production shares pools
tmopo --profile prod shares pools

# Override profile settings
tmopo -P prod --database "Other DB" shares pools
```

### Credential Priority

Credentials are resolved in this order (highest to lowest priority):

1. Command-line flags (`--token`, `--database`, `--environment`)
2. Profile from `~/.tmorc` (specified with `-P` or defaults to `demo`)
3. Environment variables (`TMO_API_TOKEN`, `TMO_DATABASE`)
4. Built-in demo credentials (for `demo` profile only)

---

## `tmoapi` - API Documentation & Config

The `tmoapi` command manages API documentation and configuration.

```bash
$ tmoapi --help
usage: tmoapi [-h] {init,download,copy,list,show} ...
```

## Where specs are stored

`tmoapi` looks for API collection files in two places, in this order:

1. `assets/postman_collection/` inside the installed package (what end users get).
2. The current working directory (handy for SDK development).

When you download or copy a collection, the CLI writes it back to
`assets/postman_collection/tmo_api_collection_YYYYMMDD.json`. During local
development this directory is resolved by walking up from the current working
directory until a `pyproject.toml` file is found.

If you want to use a different file, pass `--api-spec path/to/file.json` to the
commands that read specs.

## `tmoapi` Commands

### `init`

Initialize the `~/.tmorc` configuration file with a demo profile.

```bash
tmoapi init
tmoapi init --force  # Overwrite existing file
```

Option | Description
------ | -----------
`--force` | Overwrite existing configuration file

### `download`

Fetches the latest Postman collection from The Mortgage Office developer portal
and stores it locally.

```bash
tmoapi download
tmoapi download --output ./tmo_api_collection_latest.json
```

Option | Description
------ | -----------
`-o`, `--output` | Optional explicit destination. Without it the CLI selects the assets directory automatically and names the file after the publish date embedded in the collection.

### `copy`

Copies a collection from another location (file path or URL) into the local
assets directory. This is useful when you need to pin the SDK to an older spec
revision.

```bash
tmoapi copy ./archives/tmo_api_collection_20230901.json
tmoapi copy https://example.com/tmo_api_collection_preview.json
```

The copied file is always saved into `assets/postman_collection/`.

### `list`

Prints every endpoint contained in the current collection. The output is grouped
in a Rich table that includes the HTTP method, the folder-style name, and the
path.

```bash
tmoapi list
tmoapi list --api-spec ./tmo_api_collection_preview.json
```

Use this command when you need to find the canonical name of an endpoint before
looking up its full documentation.

### `show`

Displays detailed information about a single endpoint. You can search by the
endpoint's GUID, its name, a folder-qualified name, or even a fragment of the
URL. Rich formatting is applied to description text, headers, path variables,
query parameters, and request body snippets so you can quickly copy what you
need.

```bash
tmoapi show "Loan Origination/Create Loan"
tmoapi show 28b56336-cb43-41c6-a8b7-ec360d13a1f7
```

If multiple endpoints match your query the CLI presents them in a table and asks
you to refine the search.

!!! tip
    Pair `list` and `show` for the quickest workflow: use `tmoapi list | rg Payment`
    to find the name you care about, then `tmoapi show "<name>"` to see the
    request details.

---

## `tmopo` - Mortgage Pools Operations

The `tmopo` command provides comprehensive access to mortgage pools operations, including shares and capital pools.

```bash
$ tmopo --help
usage: tmopo [-h] [-P PROFILE] [--token TOKEN] [--database DATABASE]
             [--environment {us,usa,can,aus}] [--debug]
             [--user-agent USER_AGENT]
             {shares,capital} ...
```

### Common Options

Option | Description
------ | -----------
`-P`, `--profile` | Configuration profile to use (default: `demo`)
`--token` | API token (overrides profile)
`--database` | Database name (overrides profile)
`--environment` | API environment: `us`, `canada`, or `australia` (overrides profile)
`--debug` | Enable debug output
`--user-agent` | Override the default User-Agent header

### Shares Operations

All shares pool operations support the following actions and output options.

#### Output Options

The `shares` subcommand supports `-O` / `--output` flag to specify output file and format:

Option | Description
------ | -----------
`-O`, `--output` | Output file path. Format is auto-detected from extension: `.json`, `.csv`, `.xlsx`. If not specified, outputs as text to stdout.

**Supported Formats:**

- **Text (default)**: Human-readable table output to stdout
- **JSON** (`.json`): Raw JSON data
- **CSV** (`.csv`): Flattened CSV with intelligent handling of CustomFields
- **XLSX** (`.xlsx`): Flattened Excel spreadsheet (requires `pip install tmo-api[xlsx]`)

**CSV/XLSX Flattening:**

- Data is flattened to 2 levels deep by default
- CustomFields with Name/Value pairs are intelligently flattened into columns named `CustomFields_<Name>`
- Example: `CustomFields_Account_Number`, `CustomFields_Account_Status`, `CustomFields_Interest_Rate`
- The `raw_data` field is automatically excluded from all outputs

**Examples:**

```bash
# Text output to stdout (default)
tmopo shares pools

# JSON output to file
tmopo shares pools -O pools.json

# CSV output (flattened with CustomFields as named columns)
tmopo shares partners -O partners.csv

# Excel output (requires openpyxl)
tmopo shares pools -O pools.xlsx

# Export with date filtering
tmopo shares distributions --start-date 01/01/2024 -O distributions.csv
```

#### Pool Operations

```bash
# List all shares pools
tmopo shares pools

# Get specific pool details
tmopo shares pools-get LENDER-C
tmopo shares pools-get --pool LENDER-C

# Get pool partners
tmopo shares pools-partners LENDER-C

# Get pool loans
tmopo shares pools-loans LENDER-C

# Get pool bank accounts
tmopo shares pools-bank-accounts LENDER-C

# Get pool attachments
tmopo shares pools-attachments LENDER-C
```

#### Partner Operations

```bash
# List all partners (defaults to last 31 days)
tmopo shares partners

# List partners with date range
tmopo shares partners --start-date 01/01/2024 --end-date 12/31/2024

# Get specific partner details
tmopo shares partners-get P001002
tmopo shares partners-get --partner P001002

# Get partner attachments
tmopo shares partners-attachments P001002
```

#### Distribution Operations

```bash
# List all distributions (defaults to last 31 days)
tmopo shares distributions

# List distributions with date range
tmopo shares distributions --start-date 01/01/2024 --end-date 12/31/2024

# List distributions for specific pool
tmopo shares distributions --pool LENDER-C

# Get specific distribution details
tmopo shares distributions-get 4ABBA93E18D945CF8BC835E7512C8B8F
tmopo shares distributions-get --recid 4ABBA93E18D945CF8BC835E7512C8B8F
```

#### Certificate Operations

```bash
# List certificates (defaults to last 31 days)
tmopo shares certificates

# List certificates with date range
tmopo shares certificates --start-date 01/01/2024 --end-date 12/31/2024

# Filter by partner and pool
tmopo shares certificates --partner P001001 --pool LENDER-C
```

#### History Operations

```bash
# Get transaction history (defaults to last 31 days)
tmopo shares history

# Get history with date range
tmopo shares history --start-date 01/01/2024 --end-date 12/31/2024

# Filter by partner
tmopo shares history --partner P001001

# Filter by pool
tmopo shares history --pool LENDER-C

# Combine filters
tmopo shares history --start-date 01/01/2024 --partner P001001 --pool LENDER-C
```

### Date Filtering

For operations that support date filtering (`partners`, `distributions`, `certificates`, `history`):

- **No dates specified**: Defaults to last 31 days
- **Only start date**: End date is 31 days after start date (or today, whichever is earlier)
- **Only end date**: Start date is 31 days before end date
- **Both dates**: Uses the specified range

Date format: `MM/DD/YYYY`

### Complete Examples

```bash
# Use demo profile (default) with text output
tmopo shares pools

# Use production profile
tmopo -P production shares pools

# Export to CSV with custom date range
tmopo -P production shares partners --start-date 01/01/2024 --end-date 12/31/2024 -O partners.csv

# Export distributions to Excel
tmopo shares distributions --pool LENDER-C -O distributions.xlsx

# Get history as JSON with all filters
tmopo shares history --start-date 01/01/2024 --partner P001001 --pool LENDER-C -O history.json

# Override profile settings
tmopo -P production --database "Backup DB" shares pools -O pools.json
```

### Installation for XLSX Support

To use `.xlsx` output format, install the optional `xlsx` extra:

```bash
pip install tmo-api[xlsx]
```

This installs the required `openpyxl` library for Excel file generation.

## Exit codes

- `0` – success (including the "multiple matches" case for `show`)
- `1` – user or network error (missing file, download failure, unknown command, authentication error, etc.)
