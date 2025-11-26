import stripe

from app.config import settings

# Set API key from env; routes will validate presence
stripe.api_key = settings.STRIPE_SECRET_KEY

STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
