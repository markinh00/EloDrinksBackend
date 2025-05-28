from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationBase(BaseModel):
    customer_id: int
    title: str
    content: str
    page: str


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    page: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationRead(NotificationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_read: bool

    class Config:
        from_attributes = True
