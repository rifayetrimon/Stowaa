from pydantic import BaseModel, conint
from typing import Optional, Annotated
from datetime import datetime


class ReviewBase(BaseModel):

    rating: conint(ge=1, le=5) # type: ignore
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    product_id: int

class ReviewUpdate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True