from pydantic import BaseModel, Field


class AdminRegister(BaseModel):
    name: str
    email: str
    password: str
    confirmPassword:  str

class AdminUpdate(BaseModel):
    name: str | None = Field(default=None)
    telephone: str | None = Field(default=None)