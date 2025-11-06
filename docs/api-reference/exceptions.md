# Exceptions API Reference

## TMOException

Base exception for all TMO API errors.

```python
class TMOException(Exception):
    def __init__(
        self,
        message: str,
        error_number: Optional[int] = None
    )
```

**Attributes:**
- `message` (str): The error message
- `error_number` (Optional[int]): TMO API error number if available

## AuthenticationError

Raised for authentication failures (401/403).

```python
class AuthenticationError(TMOException):
    pass
```

**Usage:**
```python
from tmo_api import TMOClient, AuthenticationError

try:
    client = TMOClient(token="invalid", database="test")
    pools = client.shares_pools.list_all()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    if e.error_number:
        print(f"Error number: {e.error_number}")
```

## APIError

Raised when the API returns an error response.

```python
class APIError(TMOException):
    pass
```

**Usage:**
```python
from tmo_api import TMOClient, APIError

try:
    client = TMOClient(token="token", database="db")
    pool = client.shares_pools.get_pool("INVALID")
except APIError as e:
    print(f"API error: {e.message}")
    if e.error_number:
        print(f"Error number: {e.error_number}")
```

## ValidationError

Raised for client-side validation errors before making API calls.

```python
class ValidationError(TMOException):
    pass
```

**Usage:**
```python
from tmo_api import TMOClient, ValidationError

try:
    client = TMOClient(token="token", database="db")
    pool = client.shares_pools.get_pool("")  # Empty account
except ValidationError as e:
    print(f"Validation error: {e.message}")
```

## NetworkError

Raised for network/connection errors (timeouts, connection failures).

```python
class NetworkError(TMOException):
    pass
```

**Usage:**
```python
from tmo_api import TMOClient, NetworkError

try:
    client = TMOClient(token="token", database="db", timeout=1)
    pools = client.shares_pools.list_all()
except NetworkError as e:
    print(f"Network error: {e.message}")
```

## Catching All Exceptions

You can catch all TMO API exceptions using the base class:

```python
import os
from tmo_api import TMOClient, TMOException

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)

try:
    pools = client.shares_pools.list_all()
except TMOException as e:
    print(f"TMO API error: {e.message}")
    if hasattr(e, 'error_number') and e.error_number:
        print(f"Error number: {e.error_number}")
```
