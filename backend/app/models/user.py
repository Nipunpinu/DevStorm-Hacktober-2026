from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    session_token = Column(String(128), unique=True, index=True, nullable=False)
    
    # Non-sensitive demographic state stored as JSON
    profile_data_json = Column(Text, default="{}", nullable=False)
    preferred_language = Column(String(10), default="en", nullable=False)
    
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    saved_schemes = relationship("SavedScheme", back_populates="user_profile", cascade="all, delete-orphan")


class SavedScheme(Base):
    __tablename__ = "saved_schemes"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Status in user's journey: 'saved', 'documents_in_progress', 'applied_externally', 'sanctioned', 'rejected'
    application_status = Column(String(50), default="saved", nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user_profile = relationship("UserProfile", back_populates="saved_schemes")
    scheme = relationship("Scheme", back_populates="saved_by_users")

    __table_args__ = (
        Index("ix_user_scheme_unique", "user_profile_id", "scheme_id", unique=True),
    )
