from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime
from enum import Enum


# Enum for user roles
class UserRole(str, Enum):
    ADMIN = "admin"
    SELLER = "seller"
    USER = "user"
    

# shared_properties for User
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None


# Schema user registration
class UserCreate(UserBase): 
    password: str = Field(..., min_length=8, max_length=20)



# Schema for updating user details (optional fields)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=20)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_seller: Optional[bool] = None 
    role: Optional[UserRole] = None

    class Config:
        from_attributes = True


# Schema for user address
class AddressBase(BaseModel):
    street_address: str
    city: str
    state: str
    country: str
    postal_code: str
    is_default: Optional[bool] = False

    class Config:
        from_attributes = True


# Schema for creating address
class AddressCreate(AddressBase):
    pass


# Schema for address response  
class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True



# Schema user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str



# Schema for reading user details (without sensitive information)
class UserRead(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        from_attributes = True


# schema for token
class Token(BaseModel):
    access_token: str
    token_type: str


# Schema for response
class UserResponse(BaseModel):
    status: str
    message: str
    data: UserRead