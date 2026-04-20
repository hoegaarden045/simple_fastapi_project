from fastapi.params import Depends
from app.dependency import get_current_user, get_db
from app.models import User
from app.service import operations as operations_service
from app.schemas import OperationRequest
from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/operations/income")
def add_income(operation: OperationRequest, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    # Вызов сервиса для добавления дохода к балансу кошелька
    # db автоматически получается через dependency injection из get_db
    return operations_service.add_income(db, current_user, operation)

@router.post("/operations/expense")
def add_expense(operation: OperationRequest, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    # Вызов сервиса для добавления расхода (уменьшение баланса кошелька)
    # db автоматически получается через dependency injection из get_db
    return operations_service.add_expense(db, current_user, operation)
