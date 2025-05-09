from pydantic import BaseModel
from typing import List, Optional
from api.schemas.product import ProductInPack


class PackCreate(BaseModel):
    name: str
    event_type: str
    guest_count: int
    price: float
    structure_id: Optional[int] = None
    products: List[ProductInPack]


class PackRead(BaseModel):
    id: int
    name: str
    event_type: str
    guest_count: int
    price: float
    structure_id: Optional[int] = None

    class Config:
        from_attributes = True


class PackUpdate(BaseModel):
    name: str
    event_type: str
    guest_count: int
    price: float
    structure_id: Optional[int] = None
    products: Optional[List[ProductInPack]] = None
