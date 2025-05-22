from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.models.base import Base


# Banner model
class DefaultBanner(Base):
    __tablename__ = "default_banners"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=False)
    link_url = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Banner(id={self.id}, title={self.title})>"
    
# Banner 
class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=False)
    link_url = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Banner(id={self.id}, title={self.title})>"