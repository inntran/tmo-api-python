# Quick Start

This guide will help you make your first API call with the TMO API Python SDK.

## Prerequisites

Before you begin, make sure you have:

1. Installed the SDK (see [Installation](installation.md))
2. Obtained an API token and database name from The Mortgage Office
3. Know which environment to use (US, Canada, or Australia)

## Basic Usage

### Initialize the Client

First, import and initialize the client using environment variables (recommended for CI/CD):

```python
import os
from tmo_api import TMOClient, Environment

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"],
    environment=Environment.US  # or Environment.CANADA, Environment.AUSTRALIA
)
```

!!! tip "Environment Variables"
    Using environment variables is recommended for production and CI/CD environments:
    ```bash
    export TMO_API_TOKEN="your-api-token"
    export TMO_DATABASE="your-database-name"
    ```

### Get a Pool

Retrieve information about a specific mortgage pool:

```python
# Get a shares pool by account number
pool = client.shares_pools.get_pool("POOL001")

print(f"Pool Name: {pool.Name}")
print(f"Account: {pool.Account}")
print(f"Inception Date: {pool.InceptionDate}")
```

### List All Pools

Get a list of all available pools:

```python
# List all shares pools
pools = client.shares_pools.list_all()

for pool in pools:
    print(f"{pool.Account}: {pool.Name}")

# For capital pools
capital_pools = client.capital_pools.list_all()
```

### Get Partner Information

Retrieve partner account details:

```python
# Get a partner by account number (shares)
partner = client.shares_partners.get_partner("PART001")

print(f"Partner Name: {partner.get('Name')}")
print(f"Account: {partner.get('Account')}")
```

### Query Distributions

Get distribution records with optional filtering:

```python
# Get all distributions (shares)
distributions = client.shares_distributions.list_all()

# Filter by date range
distributions = client.shares_distributions.list_all(
    start_date="01/01/2024",
    end_date="12/31/2024"
)

# Filter by pool account
distributions = client.shares_distributions.list_all(
    pool_account="POOL001"
)
```

## Pool Types

The SDK supports both Shares and Capital pool types:

```python
# Shares resources (most common)
client.shares_pools
client.shares_partners
client.shares_distributions
client.shares_certificates
client.shares_history

# Capital resources
client.capital_pools
client.capital_partners
client.capital_distributions
client.capital_history
```

## Error Handling

The SDK raises specific exceptions for different error types:

```python
from tmo_api import TMOClient, AuthenticationError, APIError, ValidationError

client = TMOClient(token="your-token", database="your-db")

try:
    pool = client.shares_pools.get_pool("POOL001")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Complete Example

Here's a complete example that demonstrates various features:

```python
import os
from tmo_api import TMOClient, Environment, TMOException

def main():
    # Initialize the client with environment variables
    client = TMOClient(
        token=os.environ["TMO_API_TOKEN"],
        database=os.environ["TMO_DATABASE"],
        environment=Environment.US,
        timeout=30,  # Optional: custom timeout in seconds
        debug=True   # Optional: enable debug logging
    )
    
    try:
        # Get all pools
        print("Fetching all pools...")
        pools = client.shares_pools.list_all()
        print(f"Found {len(pools)} pools")
        
        # Get detailed information for the first pool
        if pools:
            first_pool = pools[0]
            print(f"\nPool Details:")
            print(f"  Name: {first_pool.Name}")
            print(f"  Account: {first_pool.Account}")
            
            # Get partners for this pool
            partners = client.shares_pools.get_pool_partners(first_pool.Account)
            print(f"  Partners: {len(partners)}")
            
            # Get distributions for this pool
            distributions = client.shares_distributions.list_all(
                pool_account=first_pool.Account
            )
            print(f"  Distributions: {len(distributions)}")
    
    except TMOException as e:
        print(f"Error: {e}")
        if hasattr(e, 'error_number'):
            print(f"Error Number: {e.error_number}")

if __name__ == "__main__":
    main()
```

## Next Steps

Now that you've made your first API call, explore more features:

- [Authentication](authentication.md) - Learn about authentication
- [Client](../user-guide/client.md) - Client configuration options
- [Pools](../user-guide/pools.md) - Deep dive into pool operations
- [Error Handling](../api-reference/exceptions.md) - Comprehensive error handling guide
