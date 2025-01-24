from pydantic import BaseModel
from typing import List, Optional


# schema for product base
class ProductBase(BaseModel):
    name : str
    description : Optional[str] = None  
    price : float
    stock_quantity : int
    category_id : int
    image_url : Optional[str] = None


# schema for product creation
class ProductCreate(ProductBase):
    pass


# schema for product update
class ProductUpdate(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None
    price : Optional[float] = None
    stock_quantity : Optional[int] = None
    category_id : Optional[int] = None
    image_url : Optional[str] = None


# schema for product response
class ProductResponse(ProductBase):
    id : int

    class Config:
        from_attributes = True