from pydantic import BaseModel
from typing import Optional


# Schema for category base
class CategoryBase(BaseModel):
    name: str


# Schema for category creation
class CategoryCreate(CategoryBase):
    pass  # 'user_id' should not be included here, as it's typically derived from the authenticated user


# Schema for category update
class CategoryUpdate(BaseModel):
    name: Optional[str] = None  # Made optional for flexibility during updates


# Schema for category response
class CategoryResponse(CategoryBase):
    id: int
    user_id: int  # Show the user who created the category
    name: str  # Explicitly added category_name in the response

    class Config:
        from_attributes = True

