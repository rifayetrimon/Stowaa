from pydantic import BaseModel


# schema for category base
class CategoryBase(BaseModel):
    name: str   


# schema for category creation
class CategoryCreate(CategoryBase):
    pass


# schema for category update
class CategoryUpdate(BaseModel):
    name: str


# schema for category response
class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True