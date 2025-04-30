from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class Sale(SQLModel, table=True):
    __tablename__ = "sales"
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    pack_id: Optional[int] = Field(default=None, foreign_key="packs.id")
    discount_percentage: float
    expire_date: date
    name: str
