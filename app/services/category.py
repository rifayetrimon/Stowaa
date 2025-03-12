from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryListResponse, CategoryResponse

logger = logging.getLogger(__name__)

class CategoryService:
    @staticmethod
    async def _verify_user_authorization(user: User):
        if user.role.value not in ["admin", "seller"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action"
            )

    @staticmethod
    async def create_category(db: AsyncSession, category_data: CategoryCreate, user: User):
        await CategoryService._verify_user_authorization(user)

        existing_category = await db.execute(
            select(Category).where(
                and_(
                    Category.name == category_data.name,
                    Category.user_id == user.id
                )
            )
        )
        if existing_category.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )

        new_category = Category(
            **category_data.model_dump(exclude={"user_id"}),
            user_id=user.id
        )

        try:
            db.add(new_category)
            await db.commit()
            await db.refresh(new_category)
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error"
            )

        return new_category

    @staticmethod
    async def get_categories(db: AsyncSession, user: User):
        await CategoryService._verify_user_authorization(user)
        result = await db.execute(select(Category).where(Category.user_id == user.id))
        return result.scalars().all()

    @staticmethod
    async def get_category(db: AsyncSession, category_id: int, user: User):
        await CategoryService._verify_user_authorization(user)

        result = await db.execute(
            select(Category).where(
                and_(
                    Category.id == category_id,
                    Category.user_id == user.id
                )
            )
        )
        category = result.scalar()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category

    @staticmethod
    async def update_category(db: AsyncSession, category_id: int, category_data: CategoryUpdate, user: User):
        await CategoryService._verify_user_authorization(user)

        category = await CategoryService.get_category(db, category_id, user)
        update_data = category_data.model_dump(exclude_unset=True, exclude={"user_id"})

        for key, value in update_data.items():
            setattr(category, key, value)

        try:
            await db.commit()
            await db.refresh(category)
            logger.debug(f"Updated category successfully: {category}")

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database Update Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Update failed due to database error"
            )

        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int, user: User):
        await CategoryService._verify_user_authorization(user)

        category = await CategoryService.get_category(db, category_id, user)

        try:
            await db.delete(category)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Deletion failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Deletion failed"
            )


    @staticmethod
    async def get_all_categories(db: AsyncSession, user: User):
        await CategoryService._verify_user_authorization(user)
        result = await db.execute(select(Category))
        return result.scalars().all()