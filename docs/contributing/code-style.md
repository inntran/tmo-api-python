# Code Style

## Formatting

- Use **black** for code formatting (line length: 100)
- Use **isort** for import sorting
- Follow PEP 8 guidelines

## Type Hints

All functions should have type hints:

```python
def get_pool(self, account: str) -> Pool:
    pass
```

## Documentation

Use Google-style docstrings:

```python
def get_pool(self, account: str) -> Pool:
    """Get pool details by account.
    
    Args:
        account: The pool account identifier
        
    Returns:
        Pool object with detailed information
        
    Raises:
        ValidationError: If account is invalid
    """
```

## Commit Messages

Follow conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
