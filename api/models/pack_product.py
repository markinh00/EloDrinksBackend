from typing import Optional
from sqlmodel import SQLModel, Field


class PackHasProduct(SQLModel, table=True):
    __tablename__ = "packhasproduct"

    pack_id: Optional[int] = Field(
        default=None, foreign_key="packs.id", primary_key=True
    )
    product_id: Optional[int] = Field(
        default=None, foreign_key="product.id", primary_key=True
    )
    quantity: Optional[int] = Field(default=None, nullable=False)
