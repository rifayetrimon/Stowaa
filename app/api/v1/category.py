from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryCreateResponse,
    CategoryDetailsResponse,
    CategoryUpdateResponse,
    CategoryDeleteResponse
)
from app.models.user import User
from app.api.deps import get_current_user
from app.services.category import CategoryService

router = APIRouter(
    prefix="/category",
    tags=["category"],
)

@router.post("/create", response_model=CategoryCreateResponse)
async def create_category(
    create_category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_category = await CategoryService.create_category(db, create_category, current_user)
    return CategoryCreateResponse(
        status="success",
        message="Category created successfully",
        data=CategoryResponse.model_validate(new_category)
    )

@router.get("/", response_model=CategoryListResponse)
async def get_all_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = await CategoryService.get_categories(db, current_user)
    return CategoryListResponse(
        status="success",
        message="Categories retrieved successfully",
        count=len(categories),
        data=[CategoryResponse.model_validate(c) for c in categories]
    )

@router.get("/{category_id}", response_model=CategoryDetailsResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = await CategoryService.get_category(db, category_id, current_user)
    return CategoryDetailsResponse(
        status="success",
        message="Category retrieved successfully",
        data=CategoryResponse.model_validate(category)
    )

@router.put("/{category_id}", response_model=CategoryUpdateResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_category = await CategoryService.update_category(
        db, category_id, category_update, current_user
    )
    return CategoryUpdateResponse(
        status="success",
        message="Category updated successfully",
        data=CategoryResponse.model_validate(updated_category)
    )

@router.delete("/{category_id}", response_model=CategoryDeleteResponse)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await CategoryService.delete_category(db, category_id, current_user)
    return CategoryDeleteResponse(
        status="success",
        message="Category deleted successfully"
    )