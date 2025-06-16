from pydantic import BaseModel, Field, model_validator
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Self

from api.schemas.bar_structure import BarStructureInOrder
from api.schemas.product import ProductInOrder


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
    details: Optional[str] = None


class OrderInDB(OrderCreate):
    created_at: datetime
    updated_at: datetime


class OrderInDBWithId(OrderInDB):
    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True}

class DateQueryRange(BaseModel):
    year: int | None = Field(default=None, ge=1, le=datetime.now(timezone.utc).year)
    month: int | None = Field(default=None, ge=1, le=12)

    def get_range(self):
        if self.month and self.year:
            start_date = datetime(self.year, self.month, 1)
            if self.month == 12:
                end_date = datetime(self.year + 1, 1, 1)
            else:
                end_date = datetime(self.year, self.month + 1, 1)
        else:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=30)

        return start_date, end_date

class OrderStatistics(BaseModel):
    top5_items: list[ProductInOrder]
    avg_order_value: float
    month_order_count: int
    bar_structure_percentage: list[BarStructureInOrder]

