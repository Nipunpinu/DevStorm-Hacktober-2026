from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    official_reference = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)
    
    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=utc_now, nullable=False)

    scheme = relationship("Scheme", back_populates="announcements")
