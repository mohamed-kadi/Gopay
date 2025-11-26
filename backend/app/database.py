# backend/app/database.py
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from app.config import settings

# Single engine for the app
engine = create_engine(settings.DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})


def init_db() -> None:
    # Import models so SQLModel is aware of them before creating tables
    from app.models import payment, subscription, user  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
