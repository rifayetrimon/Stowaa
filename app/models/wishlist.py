from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Wishlist(Base):
    __tablename__ = 'wishlist'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    user = relationship('User', back_populates='wishlist')
    product = relationship("Product", back_populates="wishlist")
