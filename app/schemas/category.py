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
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryCreateResponse(BaseModel):
    status: str
    message: str
    data: CategoryResponse  


class CategoryDeleteResponse(BaseModel):
    status: str
    message: str

class CategoryListResponse(BaseModel):
    status: str
    message: str
    count: int
    data: list[CategoryResponse]


class CategoryDetailsResponse(BaseModel):
    status: str
    message: str
    data: CategoryResponse


class CategoryUpdateResponse(BaseModel):
    status: str
    message: str
    data: CategoryResponse
    