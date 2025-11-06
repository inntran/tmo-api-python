# Certificates

The `CertificatesResource` provides methods for accessing certificate information.

## Methods

### get_certificates()

Get certificates with optional filtering.

```python
# All certificates
certificates = client.certificates.get_certificates()

# Filter by date range
certificates = client.certificates.get_certificates(
    start_date="01/01/2024",
    end_date="12/31/2024"
)

# Filter by partner account
certificates = client.certificates.get_certificates(
    partner_account="PART001"
)

# Filter by pool account
certificates = client.certificates.get_certificates(
    pool_account="POOL001"
)

# Combine filters
certificates = client.certificates.get_certificates(
    start_date="01/01/2024",
    end_date="12/31/2024",
    partner_account="PART001",
    pool_account="POOL001"
)
```
