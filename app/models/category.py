from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)  # <-- You need to define the id column
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    products = relationship("Product", back_populates="category")
    subcategories = relationship("Category", backref="parent", remote_side=[id])


