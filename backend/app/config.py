# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY: str | None = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")
    STRIPE_PRICE_PRO: str | None = os.getenv("STRIPE_PRICE_PRO")
    STRIPE_PRICE_ENTERPRISE: str | None = os.getenv("STRIPE_PRICE_ENTERPRISE")


settings = Settings()
