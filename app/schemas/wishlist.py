from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .product import ProductResponse

class WishlistItemBase(BaseModel):
    product_id: int

class WishlistItemCreate(WishlistItemBase):
    pass

class WishlistItemResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    product: ProductResponse

    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    items: List[WishlistItemResponse]
    total_items: int

    class Config:
        from_attributes = True


class WishlistCreateResponse(BaseModel):
    status: str
    message: str
    data: WishlistItemResponse

    class Config:
        from_attributes = True