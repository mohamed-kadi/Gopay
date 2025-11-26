# backend/app/models/subscription.py
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    stripe_subscription_id: str
    stripe_customer_id: str
    price_id: str
    status: str
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    latest_invoice_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SubscriptionCreate(SQLModel):
    price_id: str
