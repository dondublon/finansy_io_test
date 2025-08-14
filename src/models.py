from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Links(Base):
    __tablename__ = "link"

    short_url = Column(String(6), primary_key=True, index=True)
    url = Column(String(2048))
    use_counter = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
