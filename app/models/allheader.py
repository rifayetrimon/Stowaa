from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship, backref
from app.models.base import Base

# Browser catrgory
class BrowserCategory(Base):
    __tablename__ = 'browser_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    icon = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# navbar 
class Navitem(Base):
    __tablename__ = 'navitems'

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey('navitems.id', ondelete='CASCADE'), nullable=True)
    title = Column(String(100), nullable=False)
    url = Column(String(255), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)

    parent = relationship("Navitem",remote_side=[id],backref=backref("children", cascade="all, delete-orphan"))