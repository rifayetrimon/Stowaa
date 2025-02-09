from sqlalchemy import Column, Integer, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float)
    shipping_address_id = Column(Integer, ForeignKey("addresses.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    shipping_address = relationship("Address")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)  # Price at the time of purchase

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")