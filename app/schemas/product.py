
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.schemas.category import CategoryResponse
from app.schemas.review import ReviewResponse

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category_id: int
    stock_quantity: int
    sku: str
    image_url: Optional[HttpUrl] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    category: CategoryResponse
    reviews: List[ReviewResponse]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True