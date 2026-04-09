from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.dependency import get_db
from app.service import wallets as wallets_service
from app.schemas import CreateWalletRequest
from fastapi import APIRouter

router = APIRouter()

@router.get("/balance")
def get_balance(wallet_name: str | None = None, db: Session = Depends(get_db)):
    return wallets_service.get_balance(db, wallet_name)

@router.post("/wallets")
def create_wallet(wallet: CreateWalletRequest, db: Session = Depends(get_db)):
    return wallets_service.create_wallet(db, wallet)
