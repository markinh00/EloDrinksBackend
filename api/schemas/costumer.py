from pydantic import BaseModel, Field


class CostumerRegister(BaseModel):
    name: str
    telephone: str
    email: str
    password: str
    confirmPassword:  str

class CostumerRead(BaseModel):
    id: int
    name: str
    telephone: str
    email: str
    password: str

    class Config:
        from_attributes = True

class CostumerUpdate(BaseModel):
    name: str | None = Field(default=None)
    telephone: str | None = Field(default=None)