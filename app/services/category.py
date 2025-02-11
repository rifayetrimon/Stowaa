from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.redis_service import redis_service

# Cache keys
def get_cache_key_category_list(user_id: int):
    return f"user:{user_id}:categories"

def get_cache_key_category(category_id: int):
    return f"category:{category_id}"

# Get all categories with caching
async def get_categories(db: AsyncSession, user_id: int):
    cache_key = get_cache_key_category_list(user_id)
    cached_categories = await redis_service.get(cache_key)

    if cached_categories:
        return cached_categories

    result = await db.execute(select(Category).where(Category.user_id == user_id))
    categories = result.scalars().all()
    category_responses = [CategoryResponse.model_validate(category).model_dump() for category in categories]

    await redis_service.set(cache_key, category_responses)
    return category_responses

# Get a single category with caching
async def get_category(db: AsyncSession, user_id: int, category_id: int):
    cache_key = get_cache_key_category(category_id)
    cached_category = await redis_service.get(cache_key)

    if cached_category:
        return cached_category

    result = await db.execute(select(Category).where((Category.id == category_id) & (Category.user_id == user_id)))
    category = result.scalar()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category_response = CategoryResponse.model_validate(category).model_dump()
    await redis_service.set(cache_key, category_response)
    return category_response

# Create a new category
async def create_category(db: AsyncSession, user_id: int, category_in: CategoryCreate):
    existing_category = await db.execute(select(Category).where(Category.name == category_in.name, Category.user_id == user_id))
    if existing_category.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")

    new_category = Category(**category_in.model_dump(exclude_unset=True), user_id=user_id)
    try:
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        await redis_service.delete(get_cache_key_category_list(user_id))
        return CategoryResponse.model_validate(new_category)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Update an existing category
async def update_category(db: AsyncSession, user_id: int, category_id: int, category_in: CategoryUpdate):
    result = await db.execute(select(Category).where((Category.id == category_id) & (Category.user_id == user_id)))
    category = result.scalar()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in category_in.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    category.updated_at = datetime.now()
    
    try:
        await db.commit()
        await db.refresh(category)
        await redis_service.delete(get_cache_key_category(category_id))
        await redis_service.delete(get_cache_key_category_list(user_id))
        return CategoryResponse.model_validate(category)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Delete a category
async def delete_category(db: AsyncSession, user_id: int, category_id: int):
    result = await db.execute(select(Category).where((Category.id == category_id) & (Category.user_id == user_id)))
    category = result.scalar()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        await db.delete(category)
        await db.commit()
        await redis_service.delete(get_cache_key_category(category_id))
        await redis_service.delete(get_cache_key_category_list(user_id))
        return {"message": "Category deleted successfully!"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
