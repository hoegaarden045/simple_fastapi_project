from typing import Generator

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.dependency import get_db
from app.enums import CurrencyEnum
from app.models import User, Wallet
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


# объект для имитации запросов к app
@pytest.fixture()
def client():
    yield TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    # Пересоздание всех таблиц перед тестом
    Base.metadata.create_all(bind=test_engine)
    yield  # передать управление в тест
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
    user = User(login="test")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def wallet(db_session: Session, user: User) -> Wallet:
    wallet = Wallet(name="card", balance=200, user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    return wallet
