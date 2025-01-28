from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
from app.schemas.user import AddressResponse
from app.schemas.product import ProductResponse

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    price: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    shipping_address_id: int
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    shipping_address: AddressResponse
    order_items: List[OrderItemResponse]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True