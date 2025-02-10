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


class OrderFullResponse(BaseModel):
    id: int
    user_id: int
    shipping_address: AddressResponse
    total_amount: float
    status: OrderStatus
    order_items: List[OrderItemResponse]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True



class OrderResponse(BaseModel):
    status: str
    message: str
    data: OrderFullResponse

    class Config:
        from_attributes = True


class OrderList(BaseModel):
    status: str
    message: str
    count: int
    data: List[OrderFullResponse]



class OrderUpdateSchema(BaseModel):
    status: str
