from operator import and_
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate, CategoryListResponse, CategoryCreateResponse
from app.db.session import get_db
from app.models.category import Category
from app.models.user import User
from app.api.deps import get_current_user
from sqlalchemy.future import select
from datetime import datetime



router = APIRouter(
    prefix="/category",
    tags=["category"],
)


# create category
@router.post("/create", response_model=CategoryCreateResponse)
async def create_category(create_category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    elif current_user.role.value not in ["admin", "seller"]:  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to create a category")

    existing_category = await db.execute(
        select(Category).where(Category.name == create_category.name, Category.user_id == current_user.id)
    )
    if existing_category.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")

    new_category = Category(
        **create_category.model_dump(exclude={"user_id"}),
        user_id=current_user.id
    )
    
    try:
        db.add(new_category)    
        await db.commit()
        await db.refresh(new_category)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response = {
        "status" : "success",
        "message" : "Product created successfully",
        "data" : CategoryResponse.model_validate(new_category)
    }

    return response





# get all categories
@router.get("/", response_model=CategoryListResponse)
async def get_all_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    elif current_user.role.value not in ["admin", "seller"]:  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to create a category")
    result = await db.execute(select(Category).where(Category.user_id == current_user.id))
    categories = result.scalars().all()

    return {
        "status": "success",
        "message": "Categories retrieved successfully",
        "count": len(categories),
        "data": [CategoryResponse.model_validate(category) for category in categories]
    }



# get category by id
@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    elif current_user.role.value not in ["admin", "seller"]:  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to see all category")

    category = await db.execute(select(Category).where(Category.id == category_id and Category.user_id == current_user.id))
    category = category.scalar()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        user_id=category.user_id,
        status="success",
        message="Category retrieved successfully"
    )


# update category
@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category_update: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    elif current_user.role.value not in ["admin", "seller"]:  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to create a category")

    result = await db.execute(select(Category).where(Category.id == category_id, Category.user_id == current_user.id))
    category = result.scalar()

    # Check if category exists
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Update fields
    for key, value in category_update.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    # Commit changes
    db.add(category)
    await db.commit()
    await db.refresh(category)

    # Return response
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        user_id=category.user_id,
        status="success",
        message="Category updated successfully"
    )



# delete category
@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    elif current_user.role.value not in ["admin", "seller"]:  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete a category")
    
    result = await db.execute(select(Category).where(Category.id == category_id, Category.user_id == current_user.id))
    category = result.scalar()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    # Delete category properly
    await db.delete(category)  
    await db.commit()

    return {
        "status": "success",
        "message": "Category deleted successfully"
    }