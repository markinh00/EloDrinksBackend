from pydantic import BaseModel


class BarStructureCreate(BaseModel):
    name: str
    price: float


class BarStructureRead(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class BarStructureUpdate(BaseModel):
    name: str
    price: float
