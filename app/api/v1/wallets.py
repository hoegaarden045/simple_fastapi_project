from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.dependency import get_current_user, get_db
from app.models import User
from app.service import wallets as wallets_service
from app.schemas import CreateWalletRequest
from fastapi import APIRouter

router = APIRouter()

@router.get("/balance")
def get_balance(wallet_name: str | None = None, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    # Вызов сервиса для получения баланса кошелька или общего баланса
    # db автоматически получается через dependency injection из get_db
    return wallets_service.get_balance(db, current_user, wallet_name)

@router.post("/wallets")
def create_wallet(wallet: CreateWalletRequest, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    # Вызов сервиса для создания нового кошелька
    # db автоматически получается через dependency injection из get_db
    return wallets_service.create_wallet(db, current_user, wallet)
