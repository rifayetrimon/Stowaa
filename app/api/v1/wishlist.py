from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wishlist import Wishlist
from app.schemas.wishlist import WishlistItemCreate, WishlistCreateResponse, WishlistItemResponse, WishlistResponse
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

    response = {
        "status": "success",
        "message": "Product added to wishlist successfully",
        "data": WishlistItemResponse.model_validate(wishlist_item)
    }   

    return response


# view wishlist
@router.get("/", response_model=WishlistResponse)
async def get_wishlist(db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    result = await db.execute(select(Wishlist).where(Wishlist.user_id == current_user.id))
    wishlist = result.scalars().all()

    return {
        "status": "success",
        "message": "Wishlist retrieved successfully",
        "count": len(wishlist),
        "data": [WishlistItemResponse.model_validate(item) for item in wishlist]
    }



# delete wishlist
@router.delete("/{wishlist_id}")
async def delete_wishlist(wishlist_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    wishlist = await db.get(Wishlist, wishlist_id)

    if not wishlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found")
    elif wishlist.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this wishlist")

    db.delete(wishlist)
    await db.commit()

    return {
        "status": "success",
        "message": "Wishlist deleted successfully"
    }