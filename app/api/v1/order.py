from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.product import Product
from app.models.address import Address
from app.schemas.order import OrderCreate, OrderResponse
from app.api import deps


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


# create order endpoint
@router.post("/create", response_model=OrderResponse)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated!")
    
    shipping_address = await db.get(Address, order_in.shipping_address_id)
    if not shipping_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipping address not found")
    
    total_amount = 0
    order_items = []
    for item in order_in.items:
        product = await db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {item.product_id} not found")
        
        order_item = OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        total_amount += product.price * item.quantity
        order_items.append(order_item)
    
    new_order = Order(
        user_id=current_user.id,
        shipping_address_id=shipping_address.id,
        total_amount=total_amount,
        order_items=order_items
    )
    
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    
    response = {
        "status" : "success",
        "message" : "Order created successfully",
        "data" : OrderResponse.model_validate(new_order)
    }

    return response