from pydantic import BaseModel


class CartBase(BaseModel):
    product_id: int
    quantity: int


# Schema for cart creation
class CartCreate(CartBase):
    pass  


# schema for cartUpdate
class CartUpdate(BaseModel):
    quantity: int


# Schema for cart response
class CartResponse(CartBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
