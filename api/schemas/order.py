from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from bson import ObjectId


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
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),
        }
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
