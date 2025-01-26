from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.db.session import get_db
from app.models.category import Category
from app.models.user import User
from app.api.deps import get_current_user



router = APIRouter(
    prefix="/category",
    tags=["category"],
)


# create category
@router.post("/create", response_model=CategoryCreate)
async def create_category(category_in: CategoryCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_user)):
    new_category = Category(**category_in.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


