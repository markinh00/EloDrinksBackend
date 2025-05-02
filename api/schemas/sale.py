from pydantic import BaseModel
from typing import Optional
from datetime import date


class SaleCreate(BaseModel):
    name: str
    discount_percentage: float
    expire_date: date
    product_id: Optional[int] = None
    pack_id: Optional[int] = None


class SaleRead(BaseModel):
    id: int
    name: str
    discount_percentage: float
    expire_date: date
    product_id: Optional[int]
    pack_id: Optional[int]

    class Config:
        from_attributes = True


class SaleUpdate(BaseModel):
    name: str
    discount_percentage: float
    expire_date: date
    product_id: Optional[int] = None
    pack_id: Optional[int] = None
