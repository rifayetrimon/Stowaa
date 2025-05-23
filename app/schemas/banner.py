from pydantic import BaseModel

class BannerBase(BaseModel):
    id: int
    title: str
    url: str
    image: str
    order: int
    is_active: bool

class BannerCreate(BannerBase):
    pass

class BannerUpdate(BaseModel):
    title: str
    url: str
    image: str
    order: int
    is_active: bool

class BannerList(BannerBase):
    pass

class BannerResponse(BaseModel):
    id: int
    title: str
    url: str
    image: str
    order: int
    is_active: bool

    class Config:
        from_attributes = True