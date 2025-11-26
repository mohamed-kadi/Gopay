# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.database import init_db
from app.payments.routes import router as payments_router
from app.payments.webhook import router as webhook_router

app = FastAPI()

origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth_router)
app.include_router(payments_router)
app.include_router(webhook_router)


@app.on_event("startup")
def on_startup() -> None:
    # ensure tables exist before serving requests
    init_db()
