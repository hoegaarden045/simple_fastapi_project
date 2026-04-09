from fastapi.params import Depends
from app.dependency import get_db
from app.service import operations as operations_service
from app.schemas import OperationRequest
from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/operations/income")
def add_income(operation: OperationRequest, db: Session = Depends(get_db)):
    return operations_service.add_income(db, operation)

@router.post("/operations/expence")
def add_expence(operation: OperationRequest, db: Session = Depends(get_db)):
    return operations_service.add_expence(db, operation)
