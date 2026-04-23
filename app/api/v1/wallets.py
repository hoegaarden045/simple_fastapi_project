from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.dependency import get_current_user, get_db
from app.models import User
from app.service import wallets as wallets_service
from app.schemas import CreateWalletRequest, WalletResponse
from fastapi import APIRouter

router = APIRouter()


@router.get("/balance")
def get_balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Вызов сервиса для получения баланса кошелька или общего баланса, если имя не задано
    # db автоматически получается через dependency injection из get_db
    return wallets_service.get_total_balance(db, current_user)


@router.post("/wallets", response_model=WalletResponse)
def create_wallet(
    wallet: CreateWalletRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Вызов сервиса для создания нового кошелька
    # db автоматически получается через dependency injection из get_db
    return wallets_service.create_wallet(db, current_user, wallet)


@router.get("/wallets", response_model=list[WalletResponse])
def get_all_wallets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return wallets_service.get_all_wallets(db, current_user)
