# Pools

The `PoolsResource` provides methods for accessing and managing mortgage pool information.

## Overview

Pools represent mortgage pools in The Mortgage Office system. The SDK supports both Shares and Capital pool types.

## Initialization

The pools resource is automatically initialized when you create a client:

```python
import os
from tmo_api import TMOClient

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)

# Access shares pools resource
shares_pools = client.shares_pools

# Access capital pools resource
capital_pools = client.capital_pools
```

## Pool Types

```python
from tmo_api.resources.pools import PoolType

# Shares pools (default)
PoolType.SHARES

# Capital pools
PoolType.CAPITAL
```

## Methods

### get_pool()

Get detailed information about a specific pool.

**Parameters:**
- `account` (str, required): The pool account identifier

**Returns:** `Pool` object

**Example:**
```python
pool = client.shares_pools.get_pool("POOL001")

print(f"Pool Name: {pool.Name}")
print(f"Account: {pool.Account}")
print(f"Inception Date: {pool.InceptionDate}")

# Access nested objects
if pool.OtherAssets:
    for asset in pool.OtherAssets:
        print(f"Asset: {asset.Description}, Value: {asset.Value}")
```

### list_all()

Get a list of all available pools.

**Returns:** `List[Pool]`

**Example:**
```python
pools = client.shares_pools.list_all()

for pool in pools:
    print(f"{pool.Account}: {pool.Name}")
```

### get_pool_partners()

Get comprehensive financial and contact information for all partners associated with a specific pool. This includes capital activity, performance metrics, and contact details.

**Parameters:**
- `account` (str, required): The pool account identifier

**Returns:** `list` of partner dictionaries (CPartners:#TmoAPI)

**Response Fields:**
Each partner dictionary contains:

**Financial Information:**
- **BegCapital:** Beginning capital balance
- **Contributions:** Capital contributions made by the partner
- **Distributions:** Distributions paid out to the partner
- **EndCapital:** Ending capital balance for the partner
- **Income:** Income earned
- **Withdrawals:** Withdrawal amounts
- **WithdrawalsAndDisbursements:** Total withdrawals and disbursements
- **IRR:** Internal Rate of Return

**Contact Information:**
- **Account:** Partner account identifier
- **SortName:** Partner's name
- **Address:** Street, City, State, ZipCode
- **Phone:** PhoneHome, PhoneWork, PhoneCell, PhoneFax
- **EmailAddress:** Partner's email
- **TIN:** Tax Identification Number

**Other:**
- **AccountType:** Type of account
- **ERISA:** ERISA flag
- **IsACH:** ACH flag
- **RecID:** Unique record identifier

**Note:** This endpoint combines both financial transaction data and contact information. For contact/profile information only (without financial data), use `partners.get_partner()`.

**Example:**
```python
partners = client.shares_pools.get_pool_partners("LENDER-C")

for partner in partners:
    print(f"\nPartner: {partner.get('SortName')} ({partner.get('Account')})")
    print(f"  Email: {partner.get('EmailAddress')}")
    print(f"  Phone: {partner.get('PhoneHome')}")

    # Financial information
    print(f"  Beginning Capital: ${partner.get('BegCapital', 0):,.2f}")
    print(f"  Contributions: ${float(partner.get('Contributions', 0)):,.2f}")
    print(f"  Distributions: ${float(partner.get('Distributions', 0)):,.2f}")
    print(f"  Ending Capital: ${float(partner.get('EndCapital', 0)):,.2f}")
    print(f"  Income: ${float(partner.get('Income', 0)):,.2f}")
    print(f"  IRR: {partner.get('IRR', 0)}%")
```

### get_pool_loans()

Get loans associated with a pool.

**Parameters:**
- `account` (str, required): The pool account identifier

**Returns:** `list` of loan data

**Example:**
```python
loans = client.shares_pools.get_pool_loans("POOL001")

for loan in loans:
    print(f"Loan: {loan.get('LoanNumber')}")
```

### get_pool_bank_accounts()

Get bank accounts associated with a pool.

**Parameters:**
- `account` (str, required): The pool account identifier

**Returns:** `list` of bank account data

**Example:**
```python
bank_accounts = client.shares_pools.get_pool_bank_accounts("POOL001")

for account in bank_accounts:
    print(f"Bank: {account.get('BankName')}")
```

### get_pool_attachments()

Get attachments associated with a pool.

**Parameters:**
- `account` (str, required): The pool account identifier

**Returns:** `list` of attachment data

**Example:**
```python
attachments = client.shares_pools.get_pool_attachments("POOL001")

for attachment in attachments:
    print(f"File: {attachment.get('FileName')}")
```

## Pool Model

The `Pool` model represents a mortgage pool with the following key attributes:

```python
pool = client.shares_pools.get_pool("POOL001")

# Basic information
pool.rec_id          # Record ID
pool.Account         # Account number
pool.Name            # Pool name

# Date fields (automatically parsed to datetime)
pool.InceptionDate   # datetime object
pool.LastEvaluation  # datetime object
pool.SysTimeStamp    # datetime object

# Nested objects
pool.OtherAssets     # List[OtherAsset]
pool.OtherLiabilities  # List[OtherLiability]

# Access all fields dynamically
for key, value in pool.__dict__.items():
    print(f"{key}: {value}")
```

## Error Handling

```python
import os
from tmo_api import TMOClient, ValidationError, APIError

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)

try:
    pool = client.shares_pools.get_pool("INVALID")
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Common Use Cases

### 1. List All Pools with Details

```python
pools = client.shares_pools.list_all()

for pool in pools:
    print(f"\nPool: {pool.Account}")
    print(f"  Name: {pool.Name}")
    if pool.InceptionDate:
        print(f"  Inception: {pool.InceptionDate.strftime('%Y-%m-%d')}")
```

### 2. Get Complete Pool Information

```python
account = "POOL001"

# Get basic pool info
pool = client.shares_pools.get_pool(account)

# Get related data
partners = client.shares_pools.get_pool_partners(account)
loans = client.shares_pools.get_pool_loans(account)
bank_accounts = client.shares_pools.get_pool_bank_accounts(account)

print(f"Pool: {pool.Name}")
print(f"Partners: {len(partners)}")
print(f"Loans: {len(loans)}")
print(f"Bank Accounts: {len(bank_accounts)}")
```

### 3. Filter Pools by Criteria

```python
pools = client.shares_pools.list_all()

# Filter by inception date
from datetime import datetime

recent_pools = [
    p for p in pools
    if p.InceptionDate and p.InceptionDate.year >= 2024
]

print(f"Found {len(recent_pools)} pools from 2024")
```

### 4. Export Pool Data

```python
import csv

pools = client.shares_pools.list_all()

with open('pools.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Account', 'Name', 'Inception Date'])

    for pool in pools:
        writer.writerow([
            pool.Account,
            pool.Name,
            pool.InceptionDate.strftime('%Y-%m-%d') if pool.InceptionDate else ''
        ])
```

## Next Steps

- [Partners](partners.md) - Working with partners
- [Distributions](distributions.md) - Querying distributions
- [Models API Reference](../api-reference/models.md) - Pool model details
