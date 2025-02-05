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


class CardCreateResponse(BaseModel):
    status: str
    message: str
    data: CartResponse

    class Config:
        from_attributes = True



class CartListResponse(BaseModel):
    status: str
    message: str
    count: int
    data: list[CartResponse]