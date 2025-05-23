import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.models.banner import Banner, BannerType
from app.models.user import User
from app.schemas.banner import BannerCreate, BannerResponse, BannerUpdate



logger = logging.getLogger(__name__)

class BannerService:

    @staticmethod
    async def _verify_user_authorization(user: User):
        if user.role.value not in ["admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for current role"
            )
    
    @staticmethod
    async def create_banner(db: AsyncSession, banner_data: BannerCreate, user: User):
        try:
            await BannerService._verify_user_authorization(user)

            new_banner = Banner(
                **banner_data.model_dump()
            )

            db.add(new_banner)
            await db.commit()
            await db.refresh(new_banner)

            return new_banner

        except SQLAlchemyError as e:
            logger.error(f"Error creating banner: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the banner"
            )