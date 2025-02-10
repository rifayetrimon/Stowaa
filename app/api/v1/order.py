from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.product import Product
from app.models.address import Address
from app.schemas.order import OrderCreate, OrderResponse, OrderFullResponse, OrderList, OrderUpdateSchema
from app.api import deps
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.services.notification import NotificationService



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
    
    # Check shipping address exists
    shipping_address = await db.get(Address, order_in.shipping_address_id)
    if not shipping_address:
        raise HTTPException(status_code=404, detail="Shipping address not found")
    
    # Calculate total and prepare order items
    total_amount = 0
    order_items = []
    for item in order_in.items:
        product = await db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        order_item = OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        total_amount += product.price * item.quantity
        order_items.append(order_item)
    
    # Create and save the order
    new_order = Order(
        user_id=current_user.id,
        shipping_address_id=shipping_address.id,
        total_amount=total_amount,
        order_items=order_items
    )
    db.add(new_order)
    await db.commit()
    
    # Re-query the order with all relationships loaded
    result = await db.execute(
        select(Order)
        .where(Order.id == new_order.id)
        .options(
            selectinload(Order.shipping_address),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    )
    loaded_order = result.scalars().first()
    
    # Build the response
    return {
        "status": "success",
        "message": "Order created",
        "data": OrderFullResponse.model_validate(loaded_order)
    }


# payment endpoint
@router.post("/{order_id}/pay", response_model=OrderFullResponse)
async def process_payment(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    # Re-query the order with all relationships loaded
    result = await db.execute(select(Order).where(Order.id == order_id)
        .options(
            selectinload(Order.shipping_address),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    )
    loaded_order = result.scalars().first()
    
    if not loaded_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update the order status to PAID
    loaded_order.status = "paid"
    await db.commit()
    await db.refresh(loaded_order)
    
    # Build the response
    return {
        "status": "paid",
        "message": "Order paid",
        "data": OrderFullResponse.model_validate(loaded_order, from_attributes=True)
    }



# get order endpoint
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    # Re-query the order with all relationships loaded
    result = await db.execute(select(Order).where(Order.id == order_id)
        .options(
            selectinload(Order.shipping_address),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    )
    loaded_order = result.scalars().first()
    
    if not loaded_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Build the response
    return {
        "status": "success",
        "message": "Order found",
        "data": OrderFullResponse.model_validate(loaded_order)
    }



# list orders endpoint
@router.get("/", response_model=OrderList)
async def list_orders(db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    # Re-query the order with all relationships loaded
    result = await db.execute(select(Order)
        .where(Order.user_id == current_user.id)
        .options(
            selectinload(Order.shipping_address),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    )
    loaded_orders = result.scalars().all()
    
    # Build the response
    return {
        "status": "success",
        "message": "Orders found",
        "count": len(loaded_orders),
        "data": [OrderFullResponse.model_validate(order, from_attributes=True) for order in loaded_orders]

    }


# cancel order endpoint
@router.delete("/{order_id}")
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
    # Re-query the order with all relationships loaded
    result = await db.execute(select(Order).where(Order.id == order_id)
        .options(
            selectinload(Order.shipping_address),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    )
    loaded_order = result.scalars().first()
    
    if not loaded_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update the order status to CANCELLED
    loaded_order.status = "cancelled"
    await db.flush() 
    await db.commit()
    
    # Build the response
    return {
        "status": "success",
        "message": "Order cancelled"
    }


# update order status
@router.put("/{order_id}/status")
async def update_order_status(order_id: int,order_update: OrderUpdateSchema,db: AsyncSession = Depends(get_db),current_user: User = Depends(deps.get_current_user)):
    """
    Admin updates order status and sends notification to the user.
    """
    # Ensure user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get order details with user relationship loaded
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.user))  # Load the user relationship
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order status
    order.status = order_update.status
    await db.commit()

    # Notify user
    NotificationService.send_notification(
        user_email=order.user.email,  # Now accessible since user is loaded
        subject="Order Status Update",
        message=f"Your order #{order.id} status has been updated to {order.status}.",
        method="email"
    )

    return {"status": "success", "message": "Order status updated and user notified"}