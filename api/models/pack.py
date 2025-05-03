from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Field

from api.models.pack_product import PackHasProduct
from api.models.product import Product


class Pack(SQLModel, table=True):
    __tablename__ = "packs"
    id: Optional[int] = Field(default=None, primary_key=True)
    price: float
    structure_id: Optional[int] = Field(default=None, foreign_key="barstructure.id")
    name: str
    event_type: str
    guest_count: int
    products: List["Product"] = Relationship(link_model=PackHasProduct)
