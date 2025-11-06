# Partners

The `PartnersResource` provides methods for accessing partner account information.

## Overview

The SDK provides separate partner resources for Shares and Capital pool types:

```python
import os
from tmo_api import TMOClient

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)

# Access shares partners resource
shares_partners = client.shares_partners

# Access capital partners resource
capital_partners = client.capital_partners
```

## Methods

### get_partner()

Get detailed information about a specific partner. Returns a dictionary containing partner data.

**Parameters:**
- `account` (str, required): The partner account identifier

**Returns:** `Dict[str, Any]` - Partner data dictionary

**Example:**
```python
partner = client.shares_partners.get_partner("PART001")
print(f"Partner: {partner.get('Name')}")
print(f"Account: {partner.get('Account')}")
```

### get_partner_attachments()

Get attachments for a partner.

**Parameters:**
- `account` (str, required): The partner account identifier

**Returns:** `List[Any]` - List of partner attachments

**Example:**
```python
attachments = client.shares_partners.get_partner_attachments("PART001")

for attachment in attachments:
    print(f"File: {attachment.get('FileName')}")
```

### list_all()

List all partners with optional date filtering.

**Parameters:**
- `start_date` (str, optional): Start date in MM/DD/YYYY format
- `end_date` (str, optional): End date in MM/DD/YYYY format

**Returns:** `List[Any]` - List of partner data dictionaries

**Example:**
```python
# All partners
partners = client.shares_partners.list_all()

for partner in partners:
    print(f"{partner.get('Account')}: {partner.get('Name')}")

# Filter by date range
partners = client.shares_partners.list_all(
    start_date="01/01/2024",
    end_date="12/31/2024"
)
```
