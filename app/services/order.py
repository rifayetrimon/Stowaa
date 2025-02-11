from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.address import Address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.services.notification import NotificationService
from sqlalchemy.future import select


class OrderService:
    @staticmethod
    async def create_order(
        db: AsyncSession,
        order_in,
        current_user
    ):
        try:
            # Check if shipping address exists
            shipping_address = await db.get(Address, order_in.shipping_address_id)
            if not shipping_address:
                raise Exception("Shipping address not found")
            
            total_amount = 0
            order_items = []
            
            # Loop through items to build order items and calculate total amount
            for item in order_in.items:
                product = await db.get(Product, item.product_id)
                if not product:
                    raise Exception(f"Product {item.product_id} not found")
                order_item = OrderItem(
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.price
                )
                total_amount += product.price * item.quantity
                order_items.append(order_item)
            
            # Create and add the new order
            new_order = Order(
                user_id=current_user.id,
                shipping_address_id=shipping_address.id,
                total_amount=total_amount,
                order_items=order_items
            )
            db.add(new_order)
            await db.commit()
            return new_order
        
        except Exception as e:
            await db.rollback()
            raise Exception(f"Order creation failed: {str(e)}")
    
    @staticmethod
    async def process_payment(
        db: AsyncSession,
        order_id: int
    ):
        try:
            # Fetch the order
            result = await db.execute(select(Order).where(Order.id == order_id)
                .options(
                    selectinload(Order.shipping_address),
                    selectinload(Order.order_items).selectinload(OrderItem.product)
                )
            )
            loaded_order = result.scalars().first()

            if not loaded_order:
                raise Exception("Order not found")
            
            # Update the order status to 'paid'
            loaded_order.status = "paid"
            await db.commit()
            return loaded_order
        
        except Exception as e:
            await db.rollback()
            raise Exception(f"Payment processing failed: {str(e)}")
    
    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        order_id: int,
        order_update
    ):
        try:
            # Fetch order with user relationship loaded
            result = await db.execute(select(Order).where(Order.id == order_id).options(selectinload(Order.user)))
            order = result.scalars().first()

            if not order:
                raise Exception("Order not found")
            
            # Update the order status
            order.status = order_update.status
            await db.commit()

            # Send notification to the user
            NotificationService.send_notification(
                user_email=order.user.email,
                subject="Order Status Update",
                message=f"Your order #{order.id} status has been updated to {order.status}.",
                method="email"
            )

            return order
        
        except Exception as e:
            await db.rollback()
            raise Exception(f"Order status update failed: {str(e)}")
