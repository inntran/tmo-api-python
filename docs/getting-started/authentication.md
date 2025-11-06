# Authentication

The TMO API uses token-based authentication with a database identifier. This guide explains how to obtain and use your credentials with the SDK.

## Obtaining Credentials

To use the TMO API, you need to obtain credentials from The Mortgage Office:

1. Contact The Mortgage Office support
2. Request API access for your organization
3. Receive your API token and database name

!!! warning "Keep Your Credentials Secure"
    Your API token grants access to your TMO data. Never commit it to version control or share it publicly.

## Using Credentials

### Basic Authentication

Pass your credentials when initializing the client:

```python
from tmo_api import TMOClient

client = TMOClient(
    token="your-api-token",
    database="your-database-name"
)
```

### Environment Variables

For better security, store your credentials in environment variables:

```bash
export TMO_API_TOKEN="your-api-token"
export TMO_DATABASE="your-database-name"
```

Then load them in your code:

```python
import os
from tmo_api import TMOClient

token = os.environ.get("TMO_API_TOKEN")
database = os.environ.get("TMO_DATABASE")

client = TMOClient(token=token, database=database)
```

### Configuration File

You can also store your configuration in a file:

```python
import configparser
from tmo_api import TMOClient, Environment

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

token = config['tmo']['token']
database = config['tmo']['database']
environment = config['tmo']['environment']

# Initialize client
client = TMOClient(
    token=token,
    database=database,
    environment=Environment[environment.upper()]
)
```

Example `config.ini`:

```ini
[tmo]
token = your-api-token
database = your-database-name
environment = US
```

!!! danger "Never Commit Secrets"
    Add `config.ini` to your `.gitignore` to prevent accidentally committing your credentials.

## Environments

The TMO API has different endpoints for different regions:

```python
from tmo_api import Environment

# United States (default)
Environment.US

# Canada
Environment.CANADA

# Australia
Environment.AUSTRALIA
```

Specify the environment when creating the client:

```python
from tmo_api import TMOClient, Environment

client = TMOClient(
    token="your-token",
    database="your-database",
    environment=Environment.CANADA
)
```

## Custom Base URL

If you need to use a custom API endpoint (string instead of Environment enum):

```python
client = TMOClient(
    token="your-token",
    database="your-database",
    environment="https://custom.api.endpoint.com"
)
```

## Authentication Errors

The SDK will raise an `AuthenticationError` if authentication fails:

```python
from tmo_api import TMOClient, AuthenticationError

try:
    client = TMOClient(token="invalid-token", database="invalid-db")
    pools = client.shares_pools.list_all()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    if hasattr(e, 'error_number'):
        print(f"Error number: {e.error_number}")
```

Common authentication errors:

- **401 Unauthorized** - Invalid token or database name
- **403 Forbidden** - Token doesn't have required permissions

## Best Practices

### 1. Use Environment Variables

```python
import os
from tmo_api import TMOClient

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)
```

### 2. Validate Credentials at Startup

```python
def validate_credentials():
    try:
        client = TMOClient(
            token=os.environ["TMO_API_TOKEN"],
            database=os.environ["TMO_DATABASE"]
        )
        # Make a simple API call to validate
        client.shares_pools.list_all()
        return True
    except AuthenticationError:
        return False

if not validate_credentials():
    print("Error: Invalid credentials")
    exit(1)
```

### 3. Use Separate Credentials for Environments

```python
# Development
dev_client = TMOClient(
    token=os.environ["TMO_DEV_TOKEN"],
    database=os.environ["TMO_DEV_DATABASE"],
    debug=True
)

# Production
prod_client = TMOClient(
    token=os.environ["TMO_PROD_TOKEN"],
    database=os.environ["TMO_PROD_DATABASE"],
    debug=False
)
```

## Troubleshooting

### "Invalid Token" Error

- Verify the token is correct
- Check that there are no extra spaces or newlines
- Ensure you're using the correct environment

### "Invalid Database" Error

- Verify the database name is correct
- Check for typos in the database name
- Contact TMO support to verify your database name

### Environment Variable Not Found

```python
import os
from tmo_api import TMOClient

token = os.environ.get("TMO_API_TOKEN")
database = os.environ.get("TMO_DATABASE")

if not token or not database:
    raise ValueError("TMO_API_TOKEN and TMO_DATABASE environment variables must be set")

client = TMOClient(token=token, database=database)
```

## Next Steps

- [Client Configuration](../user-guide/client.md) - Advanced client options
- [Error Handling](../api-reference/exceptions.md) - Handle authentication errors
