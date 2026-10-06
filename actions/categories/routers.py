from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from actions.categories import schemas, models
from app.auth.routers import get_current_user

router = APIRouter(
    prefix='/categories',
    tags=['Categories']
)

# Add category
@router.post('/', response_model=schemas.ShowCategory)
def create_category(request: schemas.CategoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_category = models.Category(user_id=current_user.id, name=request.name, type=request.type)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# Show all categories
@router.get('/', response_model=List[schemas.ShowCategory])
def get_categories(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    categories = db.query(models.Category).filter(
        models.Category.user_id == current_user.id
    ).all()
    return categories