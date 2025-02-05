from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wishlist import Wishlist
from app.schemas.wishlist import WishlistItemCreate, WishlistCreateResponse, WishlistItemResponse
from app.db.session import get_db
from app.models.user import User
from app.api import deps
from sqlalchemy.future import select


router = APIRouter(
    prefix="/wishlist",
    tags=["wishlist"],
)


# wishlist create
@router.post("/create", response_model=WishlistCreateResponse)
async def create_wishlist(wishlist: WishlistItemCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    wishlist_item = Wishlist(**wishlist.model_dump(), user_id=current_user.id)

    db.add(wishlist_item)
    await db.commit()
    await db.refresh(wishlist_item)

    return {
        "status": "success",
        "message": "Product added to wishlist successfully",
        "data": WishlistItemResponse.model_validate(wishlist_item)
    }