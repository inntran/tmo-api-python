# Models API Reference

## BaseModel

Base class for all data models.

```python
class BaseModel:
    rec_id: Optional[int]
```

## Pool

Represents a mortgage pool.

```python
class Pool(BaseModel):
    Account: Optional[str]
    Name: Optional[str]
    InceptionDate: Optional[datetime]
    LastEvaluation: Optional[datetime]
    SysTimeStamp: Optional[datetime]
    OtherAssets: List[OtherAsset]
    OtherLiabilities: List[OtherLiability]
```

## OtherAsset

Represents an asset in a pool.

```python
class OtherAsset(BaseModel):
    Description: Optional[str]
    Value: Optional[float]
    DateLastEvaluated: Optional[datetime]
```

## OtherLiability

Represents a liability in a pool.

```python
class OtherLiability(BaseModel):
    Description: Optional[str]
    Amount: Optional[float]
    MaturityDate: Optional[datetime]
    PaymentNextDue: Optional[datetime]
```

## Response Models

### BaseResponse

```python
class BaseResponse:
    status: Optional[int]
    message: Optional[str]
    data: Any
```

### PoolResponse

```python
class PoolResponse(BaseResponse):
    pool: Optional[Pool]
```

### PoolsResponse

```python
class PoolsResponse(BaseResponse):
    pools: List[Pool]
```
