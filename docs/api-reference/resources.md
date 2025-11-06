# Resources API Reference

## PoolsResource

```python
class PoolsResource:
    def get_pool(self, account: str) -> Pool
    def list_all(self) -> List[Pool]
    def get_pool_partners(self, account: str) -> list
    def get_pool_loans(self, account: str) -> list
    def get_pool_bank_accounts(self, account: str) -> list
    def get_pool_attachments(self, account: str) -> list
```

## PartnersResource

```python
class PartnersResource:
    def get_partner(self, account: str) -> dict
    def get_partner_attachments(self, account: str) -> list
    def list_all(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> list
```

## DistributionsResource

```python
class DistributionsResource:
    def get_distribution(self, rec_id: str) -> dict
    def list_all(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        pool_account: Optional[str] = None
    ) -> list
```

## CertificatesResource

```python
class CertificatesResource:
    def get_certificates(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partner_account: Optional[str] = None,
        pool_account: Optional[str] = None
    ) -> list
```

## HistoryResource

```python
class HistoryResource:
    def get_history(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partner_account: Optional[str] = None,
        pool_account: Optional[str] = None
    ) -> list
```
