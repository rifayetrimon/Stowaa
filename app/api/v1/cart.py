from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cart import Cart
from app.schemas.cart import CartCreate, CartUpdate
from app.db.session import get_db
from app.models.user import User
from app.api import deps


router = APIRouter(
    prefix="/cart",
    tags=["cart"],
)


# cart create 
@router.post("/create", response_model=CartCreate)
async def create_cart(cart: CartCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    cart = Cart(**cart.model_dump(), user_id=current_user.id)
    db.add(cart)
    await db.commit()
    return cart