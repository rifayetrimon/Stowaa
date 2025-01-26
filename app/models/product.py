from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import Base

class Product(Base):
    __tablename__ = 'products' 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('categories.id'))
    image_url = Column(String(255)) 
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    category = relationship('Category', back_populates='products')
    user = relationship('User', back_populates='products')
