# History

The `HistoryResource` provides methods for retrieving account history.

## Methods

### get_history()

Get account history with optional filtering.

```python
# All history
history = client.history.get_history()

# Filter by date range
history = client.history.get_history(
    start_date="01/01/2024",
    end_date="12/31/2024"
)

# Filter by partner account
history = client.history.get_history(
    partner_account="PART001"
)

# Filter by pool account
history = client.history.get_history(
    pool_account="POOL001"
)

# Combine filters
history = client.history.get_history(
    start_date="01/01/2024",
    end_date="12/31/2024",
    partner_account="PART001",
    pool_account="POOL001"
)
```
