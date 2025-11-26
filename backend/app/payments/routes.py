# backend/app/payments/routes.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.auth import get_current_user
from app.config import settings
from app.database import get_session
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.user import User
from .stripe_config import stripe  # configured Stripe client

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentRequest(BaseModel):
    amount: int  # in cents
    currency: str = "usd"

class SubscriptionRequest(BaseModel):
    price_id: str


@router.post("/create-payment-intent")
def create_payment_intent(
    payment: PaymentRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe secret key not configured")
    try:
        intent = stripe.PaymentIntent.create(
            amount=payment.amount,
            currency=payment.currency,
        )

        record = Payment(
            user_id=current_user.id,
            amount=payment.amount,
            currency=payment.currency,
            stripe_payment_intent_id=intent.id,
            status=intent.status,
            created_at=datetime.now(timezone.utc),
        )
        session.add(record)
        session.commit()
        return {"client_secret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def list_my_payments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    payments = session.exec(
        select(Payment).where(Payment.user_id == current_user.id).order_by(Payment.created_at.desc())
    ).all()
    return payments


@router.post("/create-subscription")
def create_subscription(
    payload: SubscriptionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe secret key not configured")

    allowed_prices = [p for p in [settings.STRIPE_PRICE_PRO, settings.STRIPE_PRICE_ENTERPRISE] if p]
    if payload.price_id not in allowed_prices:
        raise HTTPException(status_code=400, detail="Invalid or unsupported price_id")

    # Ensure Stripe customer exists
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(email=current_user.email)
        current_user.stripe_customer_id = customer.id
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

    try:
        subscription = stripe.Subscription.create(
            customer=current_user.stripe_customer_id,
            items=[{"price": payload.price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
        )

        client_secret = None
        latest_invoice = subscription.get("latest_invoice")
        if latest_invoice and latest_invoice.get("payment_intent"):
            client_secret = latest_invoice["payment_intent"]["client_secret"]

        record = Subscription(
            user_id=current_user.id,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=current_user.stripe_customer_id,
            price_id=payload.price_id,
            status=subscription.status,
            current_period_end=datetime.fromtimestamp(subscription["current_period_end"], tz=timezone.utc)
            if subscription.get("current_period_end")
            else None,
            cancel_at_period_end=subscription.get("cancel_at_period_end", False),
            latest_invoice_id=latest_invoice["id"] if latest_invoice else None,
        )
        session.add(record)
        session.commit()
        return {"client_secret": client_secret, "subscription_id": subscription.id, "status": subscription.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
