from pydantic import BaseModel
from datetime import datetime
from typing import List
from bson import ObjectId
from pydantic import Field


class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: int


class BarStructure(BaseModel):
    id: int
    name: str
    price: float


class BudgetItem(BaseModel):
    id: int
    name: str
    quantity: int
    unit_price: float
    img_url: str
    category: str


class Budget(BaseModel):
    total_value: float
    bar_structure: BarStructure
    items: List[BudgetItem]


class DateRange(BaseModel):
    start: datetime
    end: datetime


class OrderCreate(BaseModel):
    customer: Customer
    date: DateRange
    guest_count: int
    location: str
    order_status: str
    budget: Budget


class OrderInDB(OrderCreate):
    created_at: datetime
    updated_at: datetime


class OrderInDBWithId(OrderInDB):
    id: str = Field(default_factory=lambda: str(ObjectId()))
