from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderFullResponse, OrderList, OrderUpdateSchema
from app.services.order import OrderService
from app.api import deps
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.order import Order, OrderItem


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


# create order endpoint
@router.post("/create", response_model=OrderResponse)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    try:
        new_order = await OrderService.create_order(db, order_in, current_user)
        result = await db.execute(
            select(Order)
            .where(Order.id == new_order.id)
            .options(
                selectinload(Order.shipping_address),
                selectinload(Order.order_items).selectinload(OrderItem.product)
            )
        )
        loaded_order = result.scalars().first()
        return {
            "status": "success",
            "message": "Order created",
            "data": OrderFullResponse.model_validate(loaded_order)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# payment endpoint
@router.post("/{order_id}/pay", response_model=OrderFullResponse)
async def process_payment(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    try:
        loaded_order = await OrderService.process_payment(db, order_id)
        return {
            "status": "paid",
            "message": "Order paid",
            "data": OrderFullResponse.model_validate(loaded_order, from_attributes=True)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# get order endpoint
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id)
        .options(
            selectinload(Order.shipping_address),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    )
    loaded_order = result.scalars().first()
    
    if not loaded_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "status": "success",
        "message": "Order found",
        "data": OrderFullResponse.model_validate(loaded_order)
    }


# list orders endpoint
@router.get("/", response_model=OrderList)
async def list_orders(db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    result = await db.execute(select(Order)
        .where(Order.user_id == current_user.id)
        .options(
            selectinload(Order.shipping_address),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    )
    loaded_orders = result.scalars().all()
    
    return {
        "status": "success",
        "message": "Orders found",
        "count": len(loaded_orders),
        "data": [OrderFullResponse.model_validate(order, from_attributes=True) for order in loaded_orders]
    }


# cancel order endpoint
@router.delete("/{order_id}")
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    result = await db.execute(select(Order).where(Order.id == order_id)
        .options(
            selectinload(Order.shipping_address),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    )
    loaded_order = result.scalars().first()
    
    if not loaded_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    loaded_order.status = "cancelled"
    await db.flush() 
    await db.commit()
    
    return {
        "status": "success",
        "message": "Order cancelled"
    }


# update order status
@router.put("/{order_id}/status")
async def update_order_status(order_id: int, order_update: OrderUpdateSchema, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        updated_order = await OrderService.update_order_status(db, order_id, order_update)
        return {"status": "success", "message": "Order status updated and user notified"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
