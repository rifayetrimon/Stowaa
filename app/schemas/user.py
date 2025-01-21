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


# Schema for api response (no password)
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True