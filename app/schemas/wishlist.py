from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .product import ProductResponse

class WishlistItemBase(BaseModel):
    product_id: int

class WishlistItemCreate(WishlistItemBase):
    pass

class WishlistItemUpdate(BaseModel):
    product_id: Optional[int] = None



class WishlistItemResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    product_id: int

    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    status: str
    message: str
    count: int
    data: List[WishlistItemResponse]


class WishlistCreateResponse(BaseModel):
    status: str
    message: str
    data: WishlistItemResponse
