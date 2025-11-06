"""Pool-related models for The Mortgage Office SDK."""

from typing import Any, Dict, List, Optional

from .base import BaseModel, BaseResponse


class OtherAsset(BaseModel):
    """Represents an other asset in a mortgage pool."""

    def _parse_data(self, data: Dict[str, Any]) -> None:
        super()._parse_data(data)

        # Parse dates specifically (since they need conversion)
        if "DateLastEvaluated" in data:
            self.DateLastEvaluated = self._parse_date(data.get("DateLastEvaluated"))


class OtherLiability(BaseModel):
    """Represents an other liability in a mortgage pool."""

    def _parse_data(self, data: Dict[str, Any]) -> None:
        super()._parse_data(data)

        # Parse dates specifically (since they need conversion)
        if "MaturityDate" in data:
            self.MaturityDate = self._parse_date(data.get("MaturityDate"))
        if "PaymentNextDue" in data:
            self.PaymentNextDue = self._parse_date(data.get("PaymentNextDue"))


class Pool(BaseModel):
    """Represents a mortgage pool."""

    def _parse_data(self, data: Dict[str, Any]) -> None:
        super()._parse_data(data)

        # Parse dates specifically (since they need conversion)
        if "InceptionDate" in data:
            self.InceptionDate = self._parse_date(data.get("InceptionDate"))
        if "LastEvaluation" in data:
            self.LastEvaluation = self._parse_date(data.get("LastEvaluation"))
        if "SysTimeStamp" in data:
            self.SysTimeStamp = self._parse_date(data.get("SysTimeStamp"))

        # Parse nested objects (override the raw arrays with parsed objects)
        if "OtherAssets" in data:
            self.OtherAssets: List[OtherAsset] = []
            for asset_data in data.get("OtherAssets", []):
                self.OtherAssets.append(OtherAsset(asset_data))

        if "OtherLiabilities" in data:
            self.OtherLiabilities: List[OtherLiability] = []
            for liability_data in data.get("OtherLiabilities", []):
                self.OtherLiabilities.append(OtherLiability(liability_data))


class PoolResponse(BaseResponse):
    """Response containing pool data."""

    pool: Optional["Pool"]

    def __init__(self, data: Dict[str, Any]) -> None:
        super().__init__(data)
        if self.data:
            self.pool = Pool(self.data)
        else:
            self.pool = None


class PoolsResponse(BaseResponse):
    """Response containing multiple pools."""

    def __init__(self, data: Dict[str, Any]) -> None:
        super().__init__(data)
        self.pools: List[Pool] = []

        # Handle both single pool and list of pools
        pool_data: Any = self.data
        if isinstance(pool_data, list):
            for item in pool_data:
                self.pools.append(Pool(item))
        elif isinstance(pool_data, dict) and pool_data:
            self.pools.append(Pool(pool_data))
