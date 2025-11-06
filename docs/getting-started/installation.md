# Installation

This guide will help you install the TMO API Python SDK.

## Requirements

- Python 3.9 or higher
- pip (Python package installer)

## Install from PyPI

The recommended way to install the SDK is via pip:

```bash
pip install tmo-api
```

## Install from Source

If you want to install from source or contribute to the project:

```bash
# Clone the repository
git clone https://github.com/inntran/tmo-api-python.git
cd tmo-api-python

# Install in development mode
pip install -e ".[dev]"
```

## Verify Installation

To verify that the SDK is installed correctly:

```python
import tmo_api
print(tmo_api.__version__)
```

You should see the version number printed without any errors.

## Optional Dependencies

### Development Dependencies

If you want to contribute to the project, install the development dependencies:

```bash
pip install tmo-api[dev]
```

This includes:

- pytest - Testing framework
- black - Code formatter
- flake8 - Linter
- isort - Import sorter
- mypy - Type checker

### Documentation Dependencies

To build the documentation locally:

```bash
pip install tmo-api[docs]
```

This includes:

- mkdocs - Documentation generator
- mkdocs-material - Material theme
- mike - Version management

## Next Steps

Now that you have the SDK installed, proceed to:

- [Quick Start](quickstart.md) - Make your first API call
- [Authentication](authentication.md) - Learn about authentication
