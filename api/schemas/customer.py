from typing import Self

from pydantic import BaseModel, Field, model_validator


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

class CustomerSearchParams(BaseModel):
    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    telephone: str | None = Field(default=None)
    email: str | None = Field(default=None)

    @model_validator(mode="after")
    def validate_field(self) -> Self:
        counter: int = 0
        for field, _ in self.model_dump().items():
            if self.model_dump()[field] is not None: counter = counter + 1
            if counter >= 2: raise ValueError("only one parameter can be used for search!")
        if counter == 0: raise ValueError("a parameter is needed for the search!")
        return  self


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None)
    telephone: str | None = Field(default=None)