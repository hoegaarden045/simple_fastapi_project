from sqlalchemy.orm import Session
from app.schemas import CreateWalletRequest
from app.repository import wallets as wallets_repository
from fastapi import HTTPException


def get_balance(db: Session, wallet_name: str | None = None):
    if wallet_name is None:
        wallets = wallets_repository.get_all_wallets(db)
        return {"total_balance": sum([w.balance for w in wallets])}

    if not wallets_repository.is_wallet_exist(db, wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f"wallet '{wallet_name}' no found"
        )
    
    wallet = wallets_repository.get_wallet_balance_by_name(db, wallet_name)
    return {"wallet": wallet.name, "balance": wallet.balance}


def create_wallet(db: Session, wallet: CreateWalletRequest):
    if wallets_repository.is_wallet_exist(db, wallet.name):
        raise HTTPException(
            status_code=400,
            detail=f"Wallet '{wallet.name}' already exists"
        )

    wallet = wallets_repository.create_wallet(db, wallet.name, wallet.initial_balance)

    db.commit()

    return {
        "message": f"wallet '{wallet.name}' created",
        "wallet": wallet.name,
        "balance": wallet.balance
    }
