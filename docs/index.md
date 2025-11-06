# TMO API Python SDK

Welcome to the **TMO API Python SDK** documentation. This SDK provides a clean, Pythonic interface for accessing [The Mortgage Office API](https://www.themortgageoffice.com/).

## About This Project

**TMO API Python SDK** is an independent, community-maintained wrapper for The Mortgage Office API. It provides a simple and intuitive way to interact with TMO's JSON-based web services.

!!! warning "Independent Project"
    This SDK is **not affiliated with or endorsed by Applied Business Software, Inc. (The Mortgage Office)**.

## Features

- 🚀 **Easy to use** - Simple, intuitive API design
- 🔒 **Type-safe** - Full type hints support with mypy
- 🌍 **Multi-region** - Support for US, Canada, and Australia environments
- 📦 **Comprehensive** - Complete coverage of TMO API endpoints
- ✅ **Well-tested** - 92% test coverage with 111+ tests
- 📚 **Well-documented** - Extensive documentation and examples

## Supported Resources

The SDK provides access to the following TMO API resources:

- **Pools** - Access and manage mortgage pool information (Shares/Capital)
- **Partners** - Retrieve partner account details
- **Distributions** - Query distribution records
- **Certificates** - Access certificate information
- **History** - Retrieve account history

## Quick Example

```python
import os
from tmo_api import TMOClient, Environment

# Initialize the client with environment variables
client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"],
    environment=Environment.US
)

# Get a shares pool by account
pool = client.shares_pools.get_pool("POOL001")
print(f"Pool: {pool.Name}")

# List all shares pools
pools = client.shares_pools.list_all()
print(f"Found {len(pools)} pools")
```

## Getting Started

Ready to get started? Check out the following guides:

- [Installation](getting-started/installation.md) - Install the SDK
- [Quick Start](getting-started/quickstart.md) - Your first API call
- [Authentication](getting-started/authentication.md) - How to authenticate

## Support

- 📖 [Documentation](https://inntran.github.io/tmo-api-python/)
- 🐛 [Issue Tracker](https://github.com/inntran/tmo-api-python/issues)
- 💻 [Source Code](https://github.com/inntran/tmo-api-python)

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](https://github.com/inntran/tmo-api-python/blob/main/LICENSE) file for details.

## Contact

For sponsorship, commercial inquiries, or dedicated support:

- 📧 Yinchuan Song - [songyinchuan@gmail.com](mailto:songyinchuan@gmail.com)
- 💼 GitHub - [https://github.com/inntran](https://github.com/inntran)
