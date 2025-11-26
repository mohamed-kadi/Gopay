import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

os.environ["DATABASE_URL"] = "sqlite:///./test_auth.db"

from app.main import app  # noqa: E402
from app.database import get_session  # noqa: E402


# Use a separate SQLite DB for tests
test_engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})


def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


def setup_module(_module):
    SQLModel.metadata.create_all(test_engine)


def teardown_module(_module):
    if os.path.exists("test_auth.db"):
        os.remove("test_auth.db")


client = TestClient(app)


def test_register_and_login_flow():
    payload = {"email": "tester@example.com", "password": "s3cretpass"}
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 200
    assert r.json()["message"] == "User registered"

    login = client.post("/auth/login", json=payload)
    data = login.json()
    assert login.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"
