from pydantic import BaseModel
from typing import List, Optional


# Schema for product base
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    category_id: int
    image_url: Optional[str] = None


# Schema for product creation
class ProductCreate(ProductBase):
    pass  # 'user_id' should not be included here, as it's typically derived from the authenticated user


# Schema for product update
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None


# Schema for product response
class ProductResponse(ProductBase):
    id: int
    user_id: int 
    category_name: Optional[str] = None  

    class Config:
        from_attributes = True

