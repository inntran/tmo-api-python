# Client API Reference

Complete API reference for the `TMOClient` class.

## TMOClient

```python
class TMOClient:
    def __init__(
        self,
        token: str,
        database: str,
        environment: Union[Environment, str] = Environment.US,
        timeout: int = 30,
        debug: bool = False
    )
```

### Parameters

- **token** (`str`): Your API token from The Mortgage Office  
- **database** (`str`): Your database name
- **environment** (`Union[Environment, str]`): API environment or custom URL (default: `Environment.US`)
- **timeout** (`int`): Request timeout in seconds (default: 30)
- **debug** (`bool`): Enable debug logging (default: False)

### Shares Resource Attributes

- **shares_pools**: `PoolsResource` - Shares pool operations
- **shares_partners**: `PartnersResource` - Shares partner operations
- **shares_distributions**: `DistributionsResource` - Shares distribution operations
- **shares_certificates**: `CertificatesResource` - Shares certificate operations
- **shares_history**: `HistoryResource` - Shares history operations

### Capital Resource Attributes

- **capital_pools**: `PoolsResource` - Capital pool operations
- **capital_partners**: `PartnersResource` - Capital partner operations
- **capital_distributions**: `DistributionsResource` - Capital distribution operations
- **capital_history**: `HistoryResource` - Capital history operations

### Methods

#### get(endpoint: str, params: Optional[Dict[str, Any]] = None) → Dict[str, Any]

Make a GET request.

#### post(endpoint: str, json: Optional[Dict[str, Any]] = None) → Dict[str, Any]

Make a POST request.

#### put(endpoint: str, json: Optional[Dict[str, Any]] = None) → Dict[str, Any]

Make a PUT request.

#### delete(endpoint: str) → Dict[str, Any]

Make a DELETE request.
