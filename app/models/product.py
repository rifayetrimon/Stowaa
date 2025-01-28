from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class Product(Base):
    __tablename__ = 'products' 

    name = Column(String(255), index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    sku = Column(String(50), unique=True)
    image_url = Column(String(255))
    is_active = Column(Boolean, default=True)

    # Relationships
    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    cart = relationship("Cart", back_populates="product")
    wishlist = relationship("Wishlist", back_populates="product")
