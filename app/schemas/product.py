from pydantic import BaseModel, HttpUrl, Field, field_validator, field_serializer
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    price: float = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    sku: str = Field(..., min_length=8, max_length=20, pattern=r"^[A-Z0-9-]+$")
    image_url: Optional[HttpUrl] = None
    is_active: bool = True

    @field_serializer('image_url')
    def serialize_image_url(self, image_url: Optional[HttpUrl], _info):
        return str(image_url) if image_url else None
    

class ProductCreate(ProductBase):
    @field_validator('sku')
    def validate_sku(cls, v):
        v = v.upper().strip()
        if ' ' in v:
            raise ValueError("SKU cannot contain spaces")
        return v

    # Add this new validator for image_url
    @field_validator('image_url', mode='before')
    def validate_image_url(cls, v):
        return str(v) if v else None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None

    @field_serializer('image_url')
    def serialize_image_url(self, image_url: Optional[HttpUrl], _info):
        return str(image_url) if image_url else None


class ProductResponse(ProductBase):
    id: int
    user_id: int
    updated_at: datetime

    @field_serializer('updated_at')
    def serialize_updated_at(self, dt: datetime, _info):
        return dt.isoformat()


class ProductListResponse(BaseModel):
    status: str
    message: str
    count: int
    data: List[ProductResponse]


class ProductCreateResponse(BaseModel):
    status: str
    message: str
    data: ProductResponse


class ProductDetailsResponse(BaseModel):
    status: str
    message: str
    data: ProductResponse
