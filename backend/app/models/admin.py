from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class AdminAccount(Base):
    __tablename__ = "admin_accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), default="", nullable=False)
    role = Column(String(50), default="reviewer", nullable=False)  # 'superadmin', 'reviewer', 'auditor'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    last_login = Column(DateTime, nullable=True)

    audit_logs = relationship("AdminAuditLog", back_populates="admin")


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., 'create_scheme', 'verify_source', 'import_schemes', 'publish_scheme'
    target_entity = Column(String(100), nullable=False)
    target_entity_id = Column(String(100), nullable=True)
    details_json = Column(Text, default="{}", nullable=False)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    admin = relationship("AdminAccount", back_populates="audit_logs")
