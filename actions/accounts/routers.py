from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from actions.accounts import schemas, models
from app.auth.routers import get_current_user

router = APIRouter(
    prefix='/accounts',
    tags=['Accounts']
)

# Create account
@router.post('/', response_model=schemas.ShowAccount)
def create_account(request: schemas.CreateAccount, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_account = models.Account(name=request.name, type=request.type, balance=request.balance, user_id=current_user.id)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

# Show all accounts
@router.get('/', response_model=List[schemas.ShowAccount])
def get_accounts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    accounts = db.query(models.Account).filter(models.Account.user_id == current_user.id).all()
    return accounts