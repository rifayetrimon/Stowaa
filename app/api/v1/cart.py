from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cart import Cart
from app.schemas.cart import CartCreate, CartUpdate, CardCreateResponse, CartResponse, CartListResponse
from app.db.session import get_db
from app.models.user import User
from app.api import deps
from sqlalchemy.future import select


router = APIRouter(
    prefix="/carts",
    tags=["carts"],
)


# cart create 
@router.post("/create", response_model=CardCreateResponse)
async def create_cart(cart: CartCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    cart_item = Cart(**cart.model_dump(), user_id=current_user.id)

    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item) 
   
    response = {
        "status" : "success",
        "message" : "Product created successfully",
        "data" : CartResponse.model_validate(cart_item)
    }

    return response



# view cart
@router.get("/", response_model=CartListResponse)
async def get_cart(db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    carts = result.scalars().all()

    return {
        "status": "success",
        "message": "Cart retrieved successfully",
        "count": len(carts),
        "data": [CartResponse.model_validate(item) for item in carts]
    }



# delete cart
@router.delete("/{cart_id}")
async def delete_cart(cart_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    cart = await db.get(Cart, cart_id)

    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    elif cart.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this cart")

    db.delete(cart)
    await db.commit()   

    return {
        "status": "success",
        "message": "Cart deleted successfully"
    }