from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class OfficialSource(Base):
    __tablename__ = "official_sources"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    source_name = Column(String(255), nullable=False)  # e.g., 'Gazette Notification No. 12/2026', 'Ministry Portal'
    source_type = Column(String(50), default="gazette", nullable=False)  # gazette, ministry_portal, circular, annual_report
    official_url = Column(String(500), nullable=False)
    authority_name = Column(String(255), nullable=False)
    
    retrieved_at = Column(DateTime, default=utc_now, nullable=False)
    last_checked_at = Column(DateTime, default=utc_now, nullable=False)
    
    is_accessible = Column(Boolean, default=True, nullable=False)
    http_status = Column(Integer, default=200, nullable=False)
    content_hash = Column(String(64), nullable=True)
    
    verification_status = Column(String(50), default="verified", nullable=False)  # verified, pending_review, stale, broken
    notes = Column(Text, nullable=True)

    scheme = relationship("Scheme", back_populates="sources")
    history = relationship("SourceVerificationHistory", back_populates="source", cascade="all, delete-orphan")


class SourceVerificationHistory(Base):
    __tablename__ = "source_verification_history"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("official_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    
    checked_at = Column(DateTime, default=utc_now, nullable=False)
    status_code = Column(Integer, nullable=True)
    change_detected = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    verified_by_admin = Column(String(100), nullable=True)

    source = relationship("OfficialSource", back_populates="history")
