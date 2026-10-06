from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from actions.transactions import schemas, models
from actions.accounts import models as account_models
from app.auth.routers import get_current_user

router = APIRouter(
    tags=['Transactions']
)

# Add transaction
@router.post('/accounts/{account_id}/transactions', response_model=schemas.ShowTransaction)
def add_transaction(account_id: int, request: schemas.TransactionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    account = db.query(account_models.Account).filter(
        account_models.Account.id == account_id,
        account_models.Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    new_transaction = models.Transactions(
        user_id=current_user.id,
        account_id=account_id,
        type="income" if request.amount >= 0 else "expense",
        **request.dict(),
    )
    db.add(new_transaction)
    account.balance += new_transaction.amount
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

# Show all transactions
@router.get('/transactions', response_model=List[schemas.ShowTransaction])
def get_transactions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    transactions = db.query(models.Transactions).filter(
        models.Transactions.user_id == current_user.id
    ).all()
    return transactions