# Client

The `TMOClient` class is the main entry point for interacting with The Mortgage Office API. It handles authentication, request management, and provides access to all resource endpoints.

## Initialization

### Basic Initialization (Recommended)

Using environment variables is recommended for production and CI/CD:

```python
import os
from tmo_api import TMOClient

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)
```

### With Environment

```python
import os
from tmo_api import TMOClient, Environment

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"],
    environment=Environment.US  # US, CANADA, or AUSTRALIA
)
```

### With Custom Configuration

```python
import os

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"],
    environment="https://custom.endpoint.com",  # Custom API endpoint
    timeout=60,  # Request timeout in seconds (default: 30)
    debug=True   # Enable debug logging (default: False)
)
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token` | str | Required | Your TMO API token |
| `database` | str | Required | Your database name |
| `environment` | Environment \| str | `Environment.US` | API environment or custom URL |
| `timeout` | int | 30 | Request timeout in seconds |
| `debug` | bool | False | Enable debug logging |

## Available Resources

The client provides access to resources for both Shares and Capital pool types:

### Shares Resources
```python
client.shares_pools          # Pool operations
client.shares_partners       # Partner operations
client.shares_distributions  # Distribution operations
client.shares_certificates   # Certificate operations
client.shares_history        # History operations
```

### Capital Resources
```python
client.capital_pools          # Pool operations
client.capital_partners       # Partner operations
client.capital_distributions  # Distribution operations
client.capital_history        # History operations
```

## HTTP Methods

The client provides low-level HTTP methods for direct API access:

### GET Request

```python
response = client.get("/LSS.svc/Shares/Pools")
```

### POST Request

```python
data = {"field": "value"}
response = client.post("/LSS.svc/Shares/Pools", json=data)
```

### PUT Request

```python
data = {"field": "updated_value"}
response = client.put("/LSS.svc/Shares/Pools/123", json=data)
```

### DELETE Request

```python
response = client.delete("/LSS.svc/Shares/Pools/123")
```

## Debug Mode

Enable debug mode to see detailed request/response information:

```python
import os

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"],
    debug=True
)

# This will log:
# - Request method and URL
# - Request headers (with masked sensitive data)
# - Response status
# - Response body
pools = client.shares_pools.list_all()
```

## Error Handling

The client automatically handles API errors and raises appropriate exceptions:

```python
import os
from tmo_api import TMOClient, AuthenticationError, APIError, NetworkError

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)

try:
    pools = client.shares_pools.list_all()
except AuthenticationError as e:
    # 401/403 errors
    print(f"Authentication failed: {e}")
except NetworkError as e:
    # Connection/timeout errors
    print(f"Network error: {e}")
except APIError as e:
    # Other API errors
    print(f"API error: {e.message}")
```

## Session Management

The client uses a persistent `requests.Session` for better performance:

```python
import os

# Session is automatically created and reused
client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)

# Make multiple requests efficiently
pools = client.shares_pools.list_all()
partners = client.shares_partners.list_all()
# Session is reused across requests
```

## Best Practices

### 1. Reuse Client Instances

```python
import os

# Good: Create once, use many times
client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)
pools = client.shares_pools.list_all()
partners = client.shares_partners.list_all()

# Bad: Creating new client for each request
pools = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
).shares_pools.list_all()
partners = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
).shares_partners.list_all()
```

### 2. Use Environment Variables

```python
import os

client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"]
)
```

### 3. Set Appropriate Timeouts

```python
import os

# For long-running operations
client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"],
    timeout=120  # 2 minutes
)

# For quick operations
client = TMOClient(
    token=os.environ["TMO_API_TOKEN"],
    database=os.environ["TMO_DATABASE"],
    timeout=10  # 10 seconds
)
```

### 4. Handle Errors Gracefully

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
    # Log error and handle gracefully
    logger.error(f"TMO API error: {e}")
    pools = []  # Return empty list as fallback
```

## Thread Safety

The client uses `requests.Session` which is not thread-safe. Create separate client instances for each thread:

```python
import os
import threading

def fetch_pools():
    # Create separate client for this thread
    client = TMOClient(
        token=os.environ["TMO_API_TOKEN"],
        database=os.environ["TMO_DATABASE"]
    )
    return client.shares_pools.list_all()

# Create threads with separate clients
threads = []
for i in range(5):
    t = threading.Thread(target=fetch_pools)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Next Steps

- [Pools](pools.md) - Working with mortgage pools
- [Partners](partners.md) - Managing partners
- [Distributions](distributions.md) - Querying distributions
