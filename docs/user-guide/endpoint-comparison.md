# API Endpoint Comparison Guide

This guide helps you understand the differences between similar endpoints and choose the right one for your use case.

## Partner Endpoints Comparison

These three endpoints provide different views of partner data. Understanding their differences helps you choose the right endpoint for your needs.

### Side-by-Side Comparison

| Feature | `partners.list_all()` | `partners.get_partner()` | `pools.get_pool_partners()` |
|---------|----------------------|-------------------------|----------------------------|
| **Object Type** | CPSSPartners:#TmoAPI | CPartner:#TmoAPI | CPartners:#TmoAPI |
| **Returns** | List of partners | Single partner | List of partners in pool |
| **Scope** | All partners | One partner | Partners in specific pool |
| **Filtering** | Date range | By account | By pool account |
| | | | |
| **Contact Information** | | | |
| - Name | ✓ Basic | ✓ Complete | ✓ Basic (SortName) |
| - Address | ✓ | ✓ Full + Home | ✓ |
| - Phone | ✓ | ✓ All types | ✓ All types |
| - Email | ✓ | ✓ | ✓ |
| | | | |
| **Financial Data** | | | |
| - Beginning Capital | ✗ | ✗ | ✓ |
| - Contributions | ✗ | ✗ | ✓ |
| - Distributions | ✗ | ✗ | ✓ |
| - Ending Capital | ✗ | ✗ | ✓ |
| - Income | ✗ | ✗ | ✓ |
| - Withdrawals | ✗ | ✗ | ✓ |
| - IRR | ✗ | ✗ | ✓ |
| | | | |
| **Profile Details** | | | |
| - Custom Fields | ✓ | ✓ Complete | ✗ |
| - ACH Details | ✗ | ✓ Complete | ✗ |
| - Trustee Info | ✓ Basic | ✓ Complete (RecID) | ✗ |
| - Tax Info (TIN) | ✓ | ✓ + TINType | ✓ |
| - Settings/Preferences | ✗ | ✓ | ✗ |
| | | | |
| **Timestamps** | | | |
| - DateCreated | ✓ | ✓ (SysCreatedDate) | ✗ |
| - LastChanged | ✓ | ✓ (SysTimeStamp) | ✗ |
| | | | |
| **Flags** | | | |
| - ERISA | ✓ | ✓ | ✓ |
| - IsACH | ✓ | ✗ | ✓ |
| - AccountType | ✗ | ✓ | ✓ |

### When to Use Each Endpoint

#### `partners.list_all()` - Partner Directory
**Best for:**
- Finding partners created or modified within a date range
- Bulk operations across multiple partners
- Directory listings with basic contact info
- Searching for partner accounts

**Example:**
```python
# Find all partners modified in 2024
partners = client.shares_partners.list_all(
    start_date="01/01/2024",
    end_date="12/31/2024"
)

for partner in partners:
    print(f"{partner.get('Account')}: {partner.get('FirstName')} {partner.get('LastName')}")
    print(f"  Created: {partner.get('DateCreated')}")
```

**Key Characteristics:**
- Returns multiple partners
- Includes custom fields
- Filtered by creation/modification date
- No financial data
- No ACH details

---

#### `partners.get_partner()` - Complete Profile
**Best for:**
- Viewing complete partner profile
- Getting ACH banking information for payments
- Accessing all settings and preferences
- Partner management tasks

**Example:**
```python
# Get complete profile for one partner
partner = client.shares_partners.get_partner("P001002")

print(f"Name: {partner.get('FirstName')} {partner.get('LastName')}")
print(f"Email: {partner.get('EmailAddress')}")
print(f"\nACH Information:")
print(f"  Bank: {partner.get('ACH_BankName')}")
print(f"  Account: {partner.get('ACH_AccountNumber')}")
print(f"  Routing: {partner.get('ACH_RoutingNumber')}")

print(f"\nCustom Fields:")
for field in partner.get('CustomFields', []):
    print(f"  {field['Name']}: {field['Value']}")
```

**Key Characteristics:**
- Returns single partner
- Most detailed profile information
- Complete ACH banking details
- All custom fields and settings
- No financial transaction data

---

#### `pools.get_pool_partners()` - Financial Snapshot
**Best for:**
- Viewing partner capital balances and activity
- Financial reporting for a specific pool
- Calculating returns (IRR) for pool partners
- Understanding equity positions

**Example:**
```python
# Get financial data for all partners in a pool
partners = client.shares_pools.get_pool_partners("LENDER-C")

print(f"Pool LENDER-C Partners:")
for partner in partners:
    print(f"\n{partner.get('SortName')} ({partner.get('Account')})")
    print(f"  Beginning Capital: ${partner.get('BegCapital', 0)}")
    print(f"  Contributions: ${partner.get('Contributions', 0)}")
    print(f"  Distributions: ${partner.get('Distributions', 0)}")
    print(f"  Ending Capital: ${float(partner.get('EndCapital', 0)):,.2f}")
    print(f"  IRR: {partner.get('IRR')}%")
```

**Key Characteristics:**
- Returns partners in specific pool
- Complete financial data (balances, contributions, distributions)
- Performance metrics (IRR)
- Basic contact information
- No ACH details or custom fields

---

### Combining Endpoints for Complete View

Often you'll need data from multiple endpoints:

```python
# Get complete partner information (profile + financial)
account = "P001002"
pool_account = "LENDER-C"

# 1. Get detailed profile
profile = client.shares_partners.get_partner(account)

# 2. Get financial data from pool
pool_partners = client.shares_pools.get_pool_partners(pool_account)
financial = next((p for p in pool_partners if p.get('Account') == account), None)

# 3. Display combined information
print(f"Partner Profile and Financial Summary")
print(f"=" * 50)
print(f"Name: {profile.get('FirstName')} {profile.get('LastName')}")
print(f"Email: {profile.get('EmailAddress')}")
print(f"Phone: {profile.get('PhoneHome')}")
print(f"\nACH Information:")
print(f"  Bank: {profile.get('ACH_BankName')}")
print(f"  Account: {profile.get('ACH_AccountNumber')}")

if financial:
    print(f"\nFinancial Position in Pool {pool_account}:")
    print(f"  Ending Capital: ${float(financial.get('EndCapital', 0)):,.2f}")
    print(f"  Total Contributions: ${float(financial.get('Contributions', 0)):,.2f}")
    print(f"  Total Distributions: ${float(financial.get('Distributions', 0)):,.2f}")
    print(f"  IRR: {financial.get('IRR')}%")
```

---

## Transaction History Endpoint

The `history.get_history()` endpoint serves a different purpose - it provides transaction-level detail rather than profile or balance information.

### `history.get_history()` - Transaction Detail

**Object Type:** CTransaction:#TmoAPI.Pss

**Purpose:** Get detailed transaction history showing individual share activities

**Best for:**
- Viewing transaction-level detail
- Audit trails and compliance reporting
- Understanding specific share activities over time
- Tracking certificate redemptions and issuances
- ACH transaction tracking and reconciliation

**Filtering Options:**
- Date range (start_date, end_date)
- Partner account
- Pool account
- Combine any/all filters

**Key Data Returned:**
- **Transaction Details:** Code (type), Amount, Shares, SharesBalance, SharePrice, Description
- **Dates:** DateReceived, DateDeposited, DateCreated, LastChanged
- **References:** PartnerAccount, PartnerRecId, PoolAccount, PoolRecId
- **Payment Info:** PayAccount, PayName, PayAddress
- **Certificate & ACH:** Certificate number, ACH batch/trace/transaction numbers
- **Other:** Withholding, Penalty, Drip flag, CreatedBy, Notes

**Example:**
```python
# Get transaction history for a partner in a specific period
history = client.shares_history.get_history(
    partner_account="P001002",
    pool_account="LENDER-D",
    start_date="01/01/2024",
    end_date="12/31/2024"
)

print(f"Transaction History for P001002 in 2024:")
for transaction in history:
    print(f"\n{transaction.get('DateReceived')}")
    print(f"  Type: {transaction.get('Code')}")
    print(f"  Description: {transaction.get('Description')}")
    print(f"  Amount: ${transaction.get('Amount', 0):,.2f}")
    print(f"  Shares: {transaction.get('Shares', 0):,.2f}")
    print(f"  Balance After: {transaction.get('SharesBalance', 0):,.2f}")
    if transaction.get('Certificate'):
        print(f"  Certificate: {transaction.get('Certificate')}")
```

### History vs Pool-Partners

**Pool-Partners** gives you the current financial snapshot (totals and balances):
- Total contributions to date
- Total distributions to date
- Current ending capital
- Overall IRR

**History** gives you the transaction-by-transaction detail:
- Each individual contribution with date and amount
- Each individual distribution with date and amount
- How the balance changed over time
- Who created each transaction and when

**Example - Reconciling the Two:**
```python
account = "P001002"
pool_account = "LENDER-D"

# Get summary from pool-partners
pool_partners = client.shares_pools.get_pool_partners(pool_account)
partner_summary = next((p for p in pool_partners if p.get('Account') == account), None)

# Get detail from history
history = client.shares_history.get_history(
    partner_account=account,
    pool_account=pool_account
)

# Verify transactions match summary
contributions_detail = sum(
    float(t.get('Amount', 0))
    for t in history
    if t.get('Code') == 'Contribution'
)

withdrawals_detail = sum(
    abs(float(t.get('Amount', 0)))
    for t in history
    if t.get('Code') == 'PartnerWithdrawal'
)

print(f"Reconciliation for {account}:")
print(f"\nSummary (from pool-partners):")
print(f"  Total Contributions: ${float(partner_summary.get('Contributions', 0)):,.2f}")
print(f"  Total Withdrawals: ${float(partner_summary.get('Withdrawals', 0)):,.2f}")

print(f"\nDetail (from history transactions):")
print(f"  Sum of Contribution transactions: ${contributions_detail:,.2f}")
print(f"  Sum of Withdrawal transactions: ${withdrawals_detail:,.2f}")
```

---

## Quick Decision Guide

**Need to answer these questions?**

| Question | Use This Endpoint |
|----------|------------------|
| What's this partner's email and phone? | `partners.get_partner()` |
| What's this partner's ACH bank account? | `partners.get_partner()` |
| What partners were created this month? | `partners.list_all()` |
| What's this partner's current capital balance? | `pools.get_pool_partners()` |
| How much has this partner contributed total? | `pools.get_pool_partners()` |
| What's this partner's return (IRR)? | `pools.get_pool_partners()` |
| When did this partner make their last deposit? | `history.get_history()` |
| What specific transactions occurred in Q1? | `history.get_history()` |
| Which certificate was redeemed on this date? | `history.get_history()` |

---

## Related Documentation

- [Partners Guide](partners.md) - Detailed partner endpoint documentation
- [Pools Guide](pools.md) - Detailed pools endpoint documentation
- [History Guide](history.md) - Detailed history endpoint documentation
