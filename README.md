# Gopay – FastAPI + React Payments SaaS

## Prereqs
- Python 3.11 (venv at `.venv`)
- Node 18+
- Stripe test keys (secret, publishable, webhook signing secret, price IDs)

## Backend
1) Install deps:
   ```bash
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2) Configure `.env` (in repo root):
   ```
   SECRET_KEY=your_jwt_secret
   DATABASE_URL=sqlite:///./database.db
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRICE_PRO=price_...
   STRIPE_PRICE_ENTERPRISE=price_...
   ```
3) Run API:
   ```bash
   uvicorn app.main:app --app-dir backend --reload
   ```
4) Docs: http://127.0.0.1:8000/docs
5) Webhooks (for payments/subscriptions):
   ```bash
   stripe listen --forward-to localhost:8000/webhook/
   ```

## Frontend
1) Install deps:
   ```bash
   cd frontend
   npm install
   ```
2) Use your publishable key in `src/App.js` (`loadStripe(...)`).
3) Run:
   ```bash
   npm start
   ```
4) UI includes:
   - Register/Login (stores JWT in localStorage)
   - One-time payment (PaymentIntent)
   - Subscription flow (select plan, confirm payment)

## Testing
```bash
source .venv/bin/activate
pytest backend/tests/test_auth.py
```

## Notes
- DB is SQLite by default (`database.db`); switch `DATABASE_URL` for Postgres in production.
- Webhook and Stripe features require valid test keys and the listener running.***
