# backend/app/models/payment.py
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    amount: int  # in cents
    currency: str = "usd"
    stripe_payment_intent_id: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaymentCreate(SQLModel):
    user_id: Optional[int] = None
    amount: int
    currency: str = "usd"
    stripe_payment_intent_id: str
