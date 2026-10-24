from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    official_name = Column(String(255), nullable=False)
    ministry = Column(String(255), nullable=False)
    is_central = Column(Boolean, default=True, nullable=False)
    state_or_region = Column(String(100), default="All India", nullable=False)
    category = Column(String(100), nullable=False, index=True)  # e.g., 'education', 'farmers', 'livelihood', 'disability'
    category_label = Column(String(150), default="", nullable=False)
    
    # Financial benefit estimate
    numeric_benefit_value = Column(Float, default=0.0, nullable=False)
    
    # Application & Portal
    application_method = Column(String(50), default="online", nullable=False)  # online, offline_csc, hybrid
    external_portal_name = Column(String(255), nullable=True)
    external_portal_url = Column(String(500), nullable=True)
    
    # Life-cycle & Verification
    status = Column(String(50), default="active", nullable=False, index=True)  # active, expired, withdrawn, pending_review
    is_retired = Column(Boolean, default=False, nullable=False, index=True)
    retired_year = Column(String(10), nullable=True)
    retired_reason = Column(Text, nullable=True)
    replacement_scheme_slug = Column(String(100), nullable=True)
    
    verification_status = Column(String(50), default="pending_review", nullable=False, index=True)  # verified, pending_review, unverified, stale
    last_verified_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    translations = relationship("SchemeTranslation", back_populates="scheme", cascade="all, delete-orphan")
    rules = relationship("EligibilityRule", back_populates="scheme", cascade="all, delete-orphan")
    benefits = relationship("Benefit", back_populates="scheme", cascade="all, delete-orphan")
    documents = relationship("RequiredDocument", back_populates="scheme", cascade="all, delete-orphan")
    steps = relationship("ApplicationStep", back_populates="scheme", order_by="ApplicationStep.step_order", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="scheme", cascade="all, delete-orphan")
    sources = relationship("OfficialSource", back_populates="scheme", cascade="all, delete-orphan")
    saved_by_users = relationship("SavedScheme", back_populates="scheme", cascade="all, delete-orphan")


class SchemeTranslation(Base):
    __tablename__ = "scheme_translations"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    language_code = Column(String(10), nullable=False, index=True)  # 'en', 'hi', 'mr', 'ta', 'te', 'bn', etc.
    
    localized_name = Column(String(255), nullable=False)
    localized_description = Column(Text, default="", nullable=False)
    localized_benefit_summary = Column(Text, default="", nullable=False)
    
    # Structured reasons stored as pipe or JSON formatted text for easy localization
    why_qualify_text = Column(Text, default="", nullable=False)
    why_not_qualify_text = Column(Text, default="", nullable=False)
    
    is_reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    scheme = relationship("Scheme", back_populates="translations")

    __table_args__ = (
        Index("ix_scheme_lang", "scheme_id", "language_code", unique=True),
    )


class Benefit(Base):
    __tablename__ = "benefits"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    benefit_type = Column(String(50), nullable=False)  # cash_transfer, fee_waiver, subsidy, equipment
    amount = Column(Float, default=0.0, nullable=False)
    frequency = Column(String(50), default="annual", nullable=False)  # one_time, monthly, quarterly, annual
    description = Column(Text, nullable=False)
    disbursement_method = Column(String(100), default="DBT / Direct Bank Transfer", nullable=False)

    scheme = relationship("Scheme", back_populates="benefits")


class RequiredDocument(Base):
    __tablename__ = "required_documents"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    document_code = Column(String(100), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    authority = Column(String(255), nullable=False)  # e.g., UIDAI, Tehsildar, Revenue Dept
    is_mandatory = Column(Boolean, default=True, nullable=False)
    top_up_benefit = Column(String(255), nullable=True)  # For optional boost docs
    
    steps = Column(Text, nullable=False)
    turnaround = Column(String(100), default="3 - 7 Business Days", nullable=False)
    estimated_cost = Column(String(100), default="Free / Nominal Fee", nullable=False)
    official_guide_url = Column(String(500), nullable=True)

    scheme = relationship("Scheme", back_populates="documents")


class ApplicationStep(Base):
    __tablename__ = "application_steps"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    issuing_office = Column(String(255), nullable=True)
    is_online = Column(Boolean, default=True, nullable=False)
    portal_or_form_link = Column(String(500), nullable=True)

    scheme = relationship("Scheme", back_populates="steps")
