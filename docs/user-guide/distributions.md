# Distributions

The `DistributionsResource` provides methods for querying distribution records.

## Overview

The SDK provides separate distribution resources for Shares and Capital pool types:

```python
import os
from tmo_api import TMOClient

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)

# Access shares distributions resource
shares_distributions = client.shares_distributions

# Access capital distributions resource
capital_distributions = client.capital_distributions
```

## Methods

### get_distribution()

Get a specific distribution by record ID.

**Parameters:**
- `rec_id` (str, required): The distribution record identifier

**Returns:** `Dict[str, Any]` - Distribution data dictionary

**Example:**
```python
distribution = client.shares_distributions.get_distribution("123")
print(f"Distribution ID: {distribution.get('rec_id')}")
print(f"Amount: {distribution.get('Amount')}")
```

### list_all()

List all distributions with optional filtering.

**Parameters:**
- `start_date` (str, optional): Start date in MM/DD/YYYY format
- `end_date` (str, optional): End date in MM/DD/YYYY format
- `pool_account` (str, optional): Filter by specific pool account

**Returns:** `List[Any]` - List of distribution data dictionaries

**Example:**
```python
# All distributions
distributions = client.shares_distributions.list_all()

for dist in distributions:
    print(f"Distribution: {dist.get('rec_id')} - Amount: {dist.get('Amount')}")

# Filter by date range
distributions = client.shares_distributions.list_all(
    start_date="01/01/2024",
    end_date="12/31/2024"
)

# Filter by pool account
distributions = client.shares_distributions.list_all(
    pool_account="POOL001"
)

# Combine filters
distributions = client.shares_distributions.list_all(
    start_date="01/01/2024",
    end_date="12/31/2024",
    pool_account="POOL001"
)
```
