from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.db.session import get_db
from app.models.category import Category
from app.models.user import User
from app.api.deps import get_current_user
from sqlalchemy.future import select



router = APIRouter(
    prefix="/category",
    tags=["category"],
)


# create category
@router.post("/create", response_model=CategoryCreate)
async def create_category(category_in: CategoryCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    
    new_category = Category(
        **category_in.model_dump(),
        user_id=current_user.id
    )

    try:
        db.add(new_category)    
        await db.commit()
        await db.refresh(new_category)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return new_category


# get all categories
@router.get("/", response_model=list[CategoryResponse])
async def get_all_categories(db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Category).where(Category.user_id == current_user.id))
    categories = result.scalars().all()
    return categories
