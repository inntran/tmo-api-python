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

Get detailed information about a specific partner. Returns complete profile information including contact details, ACH banking information, custom fields, and trustee information.

**Parameters:**
- `account` (str, required): The partner account identifier

**Returns:** `Dict[str, Any]` - Partner data dictionary (CPartner:#TmoAPI)

**Response Fields:**
- **Contact Information:** FirstName, LastName, MI, FullName, Salutation, EmailAddress
- **Address:** Street, City, State, ZipCode, HomeStreet, HomeCity, HomeState, HomeZipCode
- **Phone Numbers:** PhoneHome, PhoneWork, PhoneCell, PhoneFax, PhoneMain
- **ACH Details:** ACH_AccountNumber, ACH_RoutingNumber, ACH_BankName, ACH_BankAddress, ACH_AccountType, ACH_SecCode, ACH_IndividualId, ACH_IndividualName, ACH_ServiceStatus, ACH_SendDepositNotificationFlag
- **Custom Fields:** Array of custom field objects with Name, Tab, and Value properties
- **Trustee Information:** TrusteeRecID, TrusteeAccountRef, TrusteeAccountType
- **Tax Information:** TIN, TINType
- **Settings:** DeliveryOptions, PrintStatementFor, EmailFormat, Categories, Notes, UsePayee, Payee
- **Registered Shareholder:** RegisteredShareholderName, RegisteredShareholderStreet, RegisteredShareholderCity, RegisteredShareholderState, RegisteredShareholderZipCode
- **Flags:** ERISA, NonResident, HomeAddrEnabled
- **Other:** AccountType, BirthDay, SecurityHeldBy, WPC_PIN, WPC_Publish, GrowthPct
- **Holdback:** Holdback_Use, Holdback_Pct, Holdback_Ref, Holdback_RecID
- **System Fields:** RecID, SysCreatedDate, SysTimeStamp

**Note:** This endpoint returns profile and contact information but does NOT include financial transaction data (contributions, distributions, capital balances). For financial data, use `pools.get_pool_partners()`.

**Example:**
```python
partner = client.shares_partners.get_partner("P001002")

# Contact information
print(f"Name: {partner.get('FirstName')} {partner.get('LastName')}")
print(f"Email: {partner.get('EmailAddress')}")
print(f"Phone: {partner.get('PhoneHome')}")
print(f"Address: {partner.get('Street')}, {partner.get('City')}, {partner.get('State')} {partner.get('ZipCode')}")

# ACH information
print(f"ACH Bank: {partner.get('ACH_BankName')}")
print(f"ACH Account: {partner.get('ACH_AccountNumber')}")
print(f"ACH Routing: {partner.get('ACH_RoutingNumber')}")

# Custom fields
for field in partner.get('CustomFields', []):
    print(f"{field['Name']}: {field['Value']}")

# Trustee information
print(f"Trustee ID: {partner.get('TrusteeRecID')}")
print(f"Trustee Account Ref: {partner.get('TrusteeAccountRef')}")
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

List all partners with optional date filtering. Date range filters partners based on their DateCreated and LastChanged timestamps.

**Parameters:**
- `start_date` (str, optional): Start date in MM/DD/YYYY format
- `end_date` (str, optional): End date in MM/DD/YYYY format

**Returns:** `List[Any]` - List of partner data dictionaries (CPSSPartners:#TmoAPI)

**Response Fields:**
Each partner dictionary contains:
- **Account:** Partner account identifier
- **Contact Info:** FirstName, LastName, MI, SortName, EmailAddress
- **Address:** Street, City, State, ZipCode
- **Phone Numbers:** PhoneHome, PhoneWork, PhoneCell, PhoneFax, PhoneMain
- **Custom Fields:** Array of custom field objects with Name, Tab, and Value properties
- **Trustee Info:** TrusteeName, TrusteeAccount, TrusteeAccountRef, TrusteeAccountType
- **Tax Info:** TIN
- **Flags:** ERISA, IsACH, UsePayee
- **Timestamps:** DateCreated, LastChanged
- **Other:** RecID, Payee

**Example:**
```python
# All partners
partners = client.shares_partners.list_all()

for partner in partners:
    print(f"{partner.get('Account')}: {partner.get('FirstName')} {partner.get('LastName')}")
    print(f"  Email: {partner.get('EmailAddress')}")
    print(f"  Created: {partner.get('DateCreated')}")

    # Show custom fields
    for field in partner.get('CustomFields', []):
        print(f"  {field['Name']}: {field['Value']}")

# Filter by date range
partners = client.shares_partners.list_all(
    start_date="01/01/2024",
    end_date="12/31/2024"
)

print(f"Found {len(partners)} partners created/modified in 2024")
```
