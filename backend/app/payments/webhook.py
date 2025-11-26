# backend/app/payments/webhook.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from datetime import datetime, timezone

from app.database import get_session
from app.models.payment import Payment
from app.models.subscription import Subscription
from .stripe_config import STRIPE_WEBHOOK_SECRET, stripe

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("/")
async def stripe_webhook(request: Request, session: Session = Depends(get_session)):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle payment succeeded
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        payment = session.exec(
            select(Payment).where(Payment.stripe_payment_intent_id == intent["id"])
        ).first()
        if payment:
            payment.status = "succeeded"
            session.add(payment)
            session.commit()

    # Handle payment failed (optional)
    if event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        payment = session.exec(
            select(Payment).where(Payment.stripe_payment_intent_id == intent["id"])
        ).first()
        if payment:
            payment.status = "failed"
            session.add(payment)
            session.commit()

    # Handle subscription-related events
    if event["type"] in ["invoice.payment_succeeded", "invoice.payment_failed"]:
        invoice = event["data"]["object"]
        sub_id = invoice.get("subscription")
        if sub_id:
            subscription = session.exec(
                select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
            ).first()
            if subscription:
                subscription.status = "active" if event["type"] == "invoice.payment_succeeded" else "past_due"
                session.add(subscription)
                session.commit()

    if event["type"] in ["customer.subscription.updated", "customer.subscription.deleted"]:
        sub_obj = event["data"]["object"]
        subscription = session.exec(
            select(Subscription).where(Subscription.stripe_subscription_id == sub_obj["id"])
        ).first()
        if subscription:
            subscription.status = sub_obj.get("status", subscription.status)
            subscription.cancel_at_period_end = sub_obj.get("cancel_at_period_end", subscription.cancel_at_period_end)
            if sub_obj.get("current_period_end"):
                subscription.current_period_end = datetime.fromtimestamp(
                    sub_obj["current_period_end"], tz=timezone.utc
                )
            session.add(subscription)
            session.commit()

    return {"status": "success"}
