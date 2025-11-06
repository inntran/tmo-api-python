# Development Setup

## Prerequisites

- Python 3.9 or higher
- Git
- pip

## Setup

Clone the repository:

```bash
git clone https://github.com/inntran/tmo-api-python.git
cd tmo-api-python
```

Install development dependencies:

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=tmo_api --cov-report=term
```

## Code Quality

Run all checks:

```bash
# Format code
black src/tmo_api tests/

# Sort imports
isort src/tmo_api tests/

# Lint
flake8 src/tmo_api

# Type check
mypy src/tmo_api
```
