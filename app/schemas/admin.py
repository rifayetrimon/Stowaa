from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
from app.schemas.user import AddressResponse
from app.schemas.product import ProductResponse
from app.models.user import UserRole


class SellerResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AllSellersResponse(BaseModel):
    status: str
    message: str
    count: int
    data: List[SellerResponse]

    class Config:
        from_attributes = True


class ChangeUserRoleRequest(BaseModel):
    role: UserRole