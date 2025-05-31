from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional
from api.helpers.timezone import get_current_time_utc_minus_3


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    title: str
    content: str
    page: str
    created_at: datetime = Field(default_factory=get_current_time_utc_minus_3)
    updated_at: datetime = Field(default_factory=get_current_time_utc_minus_3)
    is_read: bool = Field(default=False)
