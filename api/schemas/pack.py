from pydantic import BaseModel
from typing import List, Optional


class PackCreate(BaseModel):
    name: str
    event_type: str
    guest_count: int
    price: float
    structure_id: Optional[int] = None
    product_ids: List[int]


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
    product_ids: Optional[List[int]] = None
