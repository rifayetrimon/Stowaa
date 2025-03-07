# app/schemas/user.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List

class AddressBase(BaseModel):
    street_address: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: int
    user_id: int
    
    # Required to handle ORM objects
    model_config = ConfigDict(from_attributes=True)

class AddressCreateResponse(BaseModel):
    status: str
    message: str
    data: AddressResponse

class AddressListResponse(BaseModel):
    status: str
    message: str
    count: int
    data: List[AddressResponse]