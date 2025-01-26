from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Category(Base):
    __tablename__ = 'categories'  

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  

    products = relationship('Product', back_populates='category')
    user = relationship('User', back_populates='categories')
