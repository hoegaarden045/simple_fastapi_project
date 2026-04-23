from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.repository import users as users_repository
from app.schemas import UserRequest, UserResponse, TokenResponse
from app.security import get_password_hash, verify_password, create_access_token


def create_user(db: Session, payload: UserRequest) -> UserResponse:
    if users_repository.get_user(db, payload.login):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = get_password_hash(payload.password)
    user = users_repository.create_user(db, payload.login, hashed_pw)
    db.commit()

    return UserResponse.model_validate(user)


def authenticate_user(db: Session, form_data: OAuth2PasswordRequestForm) -> TokenResponse:
    user = users_repository.get_user(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.login})

    return TokenResponse(access_token=access_token, token_type="bearer")
