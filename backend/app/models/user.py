from pydantic import EmailStr
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = True
    stripe_customer_id: Optional[str] = None


class UserCreate(SQLModel):
    email: EmailStr
    password: str


class UserLogin(SQLModel):
    email: EmailStr
    password: str
