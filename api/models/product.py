from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: float
    category: str
    img_url: str
