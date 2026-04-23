from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from app.database import SessionLocal
from app.models import User
from app.repository import users as users_repository
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = users_repository.get_user(db, login=login)
    if user is None:
        raise credentials_exception

    return user
