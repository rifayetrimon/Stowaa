from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class Address(Base):
    __tablename__ = "addresses"

    user_id = Column(Integer, ForeignKey("users.id"))
    street_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100)) 
    postal_code = Column(String(20))
    country = Column(String(100))
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")