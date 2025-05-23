from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.models.base import Base

class BannerType(Enum):
    DEFAULT = "default"  # For DefaultBanners
    REGULAR = "regular"  # For regular Banners

class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=False)
    banner_type = Column(Enum(BannerType), nullable=False, default=BannerType.REGULAR)  # 👈 New field
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Banner(id={self.id}, title={self.title}, type={self.banner_type})>"