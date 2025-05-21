from typing import Optional
from pydantic import BaseModel
from datetime import datetime


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