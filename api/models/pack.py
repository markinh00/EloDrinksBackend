from typing import Optional
from sqlmodel import SQLModel, Field


class Pack(SQLModel, table=True):
    __tablename__ = "packs"
    id: Optional[int] = Field(default=None, primary_key=True)
    price: float
    structure_id: Optional[int] = Field(default=None, foreign_key="barstructure.id")
    name: str
    event_type: str
    guest_count: int
