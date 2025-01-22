from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# shared_properties for User
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Schema user registration
class UserCreate(UserBase): 
    password: str = Field(..., min_length=8, max_length=20)


# Schema user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema for updating user details (optional fields)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=20)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

    class Config:
        from_attributes = True


# Schema for api response (no password)
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


# Schema for reading user details (without sensitive information)
class UserRead(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# schema for token
class Token(BaseModel):
    access_token: str
    token_type: str