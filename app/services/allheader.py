import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from app.models.allheader import BrowserCategory
from app.models.user import User
from app.schemas.allheader import BrowserCategoryCreate, BrowserCategoryResponse, BrowserCategoryUpdate

  
logger = logging.getLogger(__name__)

class BrowserCategoryService:

    @staticmethod
    async def _verify_user_authorization(user: User):
        if user.role.value not in ["admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for current role"
            )
        
    @staticmethod
    async def create_browser_category(db: AsyncSession, category_data: BrowserCategoryCreate, user: User):
        try:
            await BrowserCategoryService._verify_user_authorization(user)

            new_category = BrowserCategory(
                **category_data.model_dump()
            )

            db.add(new_category)
            await db.commit()
            await db.refresh(new_category)

            return new_category

        except SQLAlchemyError as e:
            logger.error(f"Error creating browser category: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the browser category"
            )
        

    @staticmethod
    async def get_browser_categories(db: AsyncSession, user: User):
        try:
        
            result = await db.execute(select(BrowserCategory))
            categories = result.scalars().all()

            return [
                BrowserCategoryResponse.model_validate(category)
                for category in categories
            ]

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving browser categories: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving the browser categories"
            )
    

    @staticmethod
    async def update_browser_category(db: AsyncSession, category_id: int, category_data: BrowserCategoryUpdate, user: User):
        try:
            await BrowserCategoryService._verify_user_authorization(user)

            category = await db.execute(
                select(BrowserCategory).where(BrowserCategory.id == category_id)
            )
            category = category.scalar_one_or_none()

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Browser category not found"
                )

            for key, value in category_data.model_dump().items():
                setattr(category, key, value)

            db.add(category)
            await db.commit()
            await db.refresh(category)

            return category

        except SQLAlchemyError as e:
            logger.error(f"Error updating browser category: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the browser category"
            )