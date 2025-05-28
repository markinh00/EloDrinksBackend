from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    title: str
    content: str
    page: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_read: bool = Field(default=False)
