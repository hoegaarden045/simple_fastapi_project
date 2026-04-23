from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.dependency import get_db
from app.enums import CurrencyEnum
from app.models import User, Wallet
from app.security import get_password_hash, create_access_token
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def get_test_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db


@pytest.fixture()
def client():
    yield TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def user(db_session: Session) -> User:
    hashed_pw = get_password_hash("testpassword")
    user = User(login="test", hashed_password=hashed_pw)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def auth_headers(user: User) -> dict:
    token = create_access_token(data={"sub": user.login})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def wallet(db_session: Session, user: User) -> Wallet:
    wallet = Wallet(name="card", balance=200, user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    return wallet
