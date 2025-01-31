from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None   
    user_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    status: str
    message: str    
    id: int

    class Config:
        from_attributes = True


class CategoryDeleteResponse(BaseModel):
    status: str
    message: str