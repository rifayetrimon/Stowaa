import logging
from app.services.banner import BannerService
from app.models.user import User
from app.schemas.banner import BannerCreate, BannerResponse, BannerUpdate
from app.models.banner import Banner
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.session import get_db
from app.api.deps import get_current_user



router = APIRouter(prefix="/banner", tags=["banner"])
logger = logging.getLogger(__name__)

# create banner
@router.post("/create", response_model=BannerResponse)
async def create_banner(
    create_banner: BannerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_banner = await BannerService.create_banner(db, create_banner, current_user)
    return new_banner
