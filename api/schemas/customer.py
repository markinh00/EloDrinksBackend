from pydantic import BaseModel, Field


class CustomerRegister(BaseModel):
    name: str
    telephone: str
    email: str
    password: str
    confirmPassword:  str

class CustomerRead(BaseModel):
    id: int
    name: str
    telephone: str
    email: str
    password: str

    class Config:
        from_attributes = True

class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None)
    telephone: str | None = Field(default=None)