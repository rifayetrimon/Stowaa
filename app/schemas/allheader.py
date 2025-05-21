from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


# Schemas for browser category 
class BrowserCategory(BaseModel):
    id: int
    name: str
    icon : str

class BrowserCategoryCreate(BrowserCategory):
    pass

class BrowserCategoryUpdate(BaseModel):
    name: str
    icon : str

class BrowserCategoryList(BrowserCategory):
    pass

class BrowserCategoryResponse(BaseModel):
    id: int
    name: str
    icon: str  
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schemas for navbar 
class NavitemBase(BaseModel):
    id: int
    parent_id: Optional[int]
    title: str
    url: Optional[str]
    order: int
    is_active: bool

class NavitemCreate(NavitemBase):
    pass

class NavitemUpdate(BaseModel):
    title : Optional[str] = None
    url : Optional[str] = None
    parent_id : Optional[int] = None
    order : Optional[int] = None
    is_active : Optional[bool] = None

class NavitemOut(NavitemBase):
    id: int
    children: List['NavitemOut'] = []

    class Config:
        from_attributes = True

NavitemOut.model_rebuild()