from sqlalchemy import Column, DateTime, Integer, String, func
from app.models.base import Base

class BrowserCategory(Base):
    __tablename__ = 'browser_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    icon = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    