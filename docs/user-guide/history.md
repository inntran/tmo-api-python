# History

The `HistoryResource` provides methods for retrieving share transaction history. This includes detailed records of all share activities such as contributions, withdrawals, distributions, and certificate redemptions.

## Overview

The SDK provides separate history resources for Shares and Capital pool types:

```python
import os
from tmo_api import TMOClient

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)

# Access shares history resource
shares_history = client.shares_history

# Access capital history resource
capital_history = client.capital_history
```

## Methods

### get_history()

Get share transaction history with optional filtering. Returns detailed transaction records for share activities including contributions, withdrawals, distributions, and certificate redemptions.

**Parameters:**
- `start_date` (str, optional): Start date for filtering (MM/DD/YYYY format)
- `end_date` (str, optional): End date for filtering (MM/DD/YYYY format)
- `partner_account` (str, optional): Partner account filter
- `pool_account` (str, optional): Pool account filter

**Returns:** `List[Any]` - List of transaction dictionaries (CTransaction:#TmoAPI.Pss)

**Response Fields:**
Each transaction dictionary contains:

**Transaction Details:**
- **Code:** Transaction type (e.g., "PartnerWithdrawal", "Contribution", "Distribution")
- **Amount:** Transaction amount (negative for withdrawals)
- **Shares:** Number of shares involved (negative for redemptions)
- **SharesBalance:** Remaining share balance after transaction
- **SharePrice:** Price per share
- **ShareCost:** Cost basis per share
- **Description:** Transaction description

**Dates and Tracking:**
- **DateReceived:** When transaction was received
- **DateDeposited:** When funds were deposited
- **DateCreated:** When record was created
- **LastChanged:** Last modification timestamp
- **CreatedBy:** User who created the transaction

**Partner and Pool References:**
- **PartnerAccount:** Partner's account number
- **PartnerRecId:** Partner's record ID
- **PoolAccount:** Pool's account number
- **PoolRecId:** Pool's record ID

**Payment Information:**
- **PayAccount:** Payee account number
- **PayName:** Payee name
- **PayAddress:** Payee address

**Certificate and ACH:**
- **Certificate:** Certificate number
- **ACH_BatchNumber:** ACH batch number
- **ACH_TraceNumber:** ACH trace number
- **ACH_TransNumber:** ACH transaction number

**Other:**
- **Withholding:** Tax withholding amount
- **Penalty:** Penalty amount
- **Drip:** DRIP (Dividend Reinvestment Plan) flag
- **Reference:** Reference information
- **Notes:** Additional notes
- **TrustFundAccountRecId:** Trust fund account reference
- **RecId:** Unique transaction record ID

**Examples:**

```python
# All history
history = client.shares_history.get_history()

for transaction in history:
    print(f"Date: {transaction.get('DateReceived')}")
    print(f"Type: {transaction.get('Code')}")
    print(f"Amount: ${transaction.get('Amount', 0):,.2f}")
    print(f"Shares: {transaction.get('Shares', 0):,.2f}")
    print(f"Balance: {transaction.get('SharesBalance', 0):,.2f}")

# Filter by date range
history = client.shares_history.get_history(
    start_date="01/01/2024",
    end_date="12/31/2024"
)

# Filter by partner account
history = client.shares_history.get_history(
    partner_account="P001002"
)

# Filter by pool account
history = client.shares_history.get_history(
    pool_account="LENDER-D"
)

# Combine filters - Get all transactions for a specific partner in a specific pool during a date range
history = client.shares_history.get_history(
    start_date="01/01/2024",
    end_date="12/31/2024",
    partner_account="P001002",
    pool_account="LENDER-D"
)

# Analyze withdrawals
withdrawals = [t for t in history if t.get('Code') == 'PartnerWithdrawal']
total_withdrawn = sum(float(t.get('Amount', 0)) for t in withdrawals)
print(f"Total Withdrawals: ${abs(total_withdrawn):,.2f}")

# Track certificate redemptions
redemptions = [t for t in history if 'Redeem' in t.get('Description', '')]
for redemption in redemptions:
    print(f"Certificate {redemption.get('Certificate')} - {redemption.get('Description')}")
    print(f"  Amount: ${redemption.get('Amount', 0):,.2f}")
    print(f"  Shares: {redemption.get('Shares', 0):,.2f}")
```

## Common Use Cases

### 1. Transaction Summary Report

```python
history = client.shares_history.get_history(
    start_date="01/01/2024",
    end_date="12/31/2024",
    pool_account="LENDER-D"
)

# Group by transaction type
from collections import defaultdict
by_type = defaultdict(list)

for transaction in history:
    code = transaction.get('Code')
    by_type[code].append(transaction)

# Summary
for code, transactions in by_type.items():
    total = sum(float(t.get('Amount', 0)) for t in transactions)
    print(f"{code}: {len(transactions)} transactions, Total: ${total:,.2f}")
```

### 2. Partner Activity Report

```python
history = client.shares_history.get_history(
    partner_account="P001002",
    start_date="01/01/2024",
    end_date="12/31/2024"
)

print(f"Transaction history for partner P001002:")
for transaction in history:
    print(f"\n{transaction.get('DateReceived')}")
    print(f"  {transaction.get('Description')}")
    print(f"  Amount: ${transaction.get('Amount', 0):,.2f}")
    print(f"  Shares: {transaction.get('Shares', 0):,.2f}")
    print(f"  Balance: {transaction.get('SharesBalance', 0):,.2f}")
    if transaction.get('Certificate'):
        print(f"  Certificate: {transaction.get('Certificate')}")
```

### 3. ACH Transaction Tracking

```python
history = client.shares_history.get_history(
    start_date="01/01/2024",
    end_date="12/31/2024"
)

# Filter ACH transactions
ach_transactions = [
    t for t in history
    if t.get('ACH_BatchNumber') or t.get('ACH_TraceNumber')
]

print(f"Found {len(ach_transactions)} ACH transactions")
for transaction in ach_transactions:
    print(f"\nDate: {transaction.get('DateDeposited')}")
    print(f"  Payee: {transaction.get('PayName')}")
    print(f"  Amount: ${transaction.get('Amount', 0):,.2f}")
    print(f"  Batch: {transaction.get('ACH_BatchNumber')}")
    print(f"  Trace: {transaction.get('ACH_TraceNumber')}")
```

### 4. Export to CSV

```python
import csv

history = client.shares_history.get_history(
    start_date="01/01/2024",
    end_date="12/31/2024",
    pool_account="LENDER-D"
)

with open('transaction_history.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Date', 'Type', 'Description', 'Partner', 'Amount',
        'Shares', 'Balance', 'Certificate', 'Created By'
    ])

    for transaction in history:
        writer.writerow([
            transaction.get('DateReceived'),
            transaction.get('Code'),
            transaction.get('Description'),
            transaction.get('PartnerAccount'),
            transaction.get('Amount'),
            transaction.get('Shares'),
            transaction.get('SharesBalance'),
            transaction.get('Certificate'),
            transaction.get('CreatedBy')
        ])
```

## Next Steps

- [Partners](partners.md) - Working with partners
- [Pools](pools.md) - Working with pools
- [Distributions](distributions.md) - Querying distributions
- [Certificates](certificates.md) - Managing certificates
```
