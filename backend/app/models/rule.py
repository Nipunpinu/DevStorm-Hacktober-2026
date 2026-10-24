from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_code = Column(String(100), nullable=False)
    
    # Target profile field to check
    # Examples: 'gender', 'age_group', 'marital_status', 'state', 'region_type', 'social_category',
    #           'minority', 'disability_percentage', 'student_status', 'education_level', 'bpl_status', 'max_income'
    field_name = Column(String(100), nullable=False, index=True)
    
    # Comparison operator: 'eq', 'in', 'lte', 'gte', 'ne', 'contains'
    operator = Column(String(20), default="eq", nullable=False)
    
    # Value to compare against (string, comma-separated list, or json string)
    target_value = Column(String(255), nullable=False)
    
    # Whether failure to meet this rule is a hard disqualifier
    is_mandatory = Column(Boolean, default=True, nullable=False)
    
    # Human-readable explanation of the condition
    description = Column(Text, nullable=False)
    
    # Failure message if profile does not satisfy condition
    failure_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)

    scheme = relationship("Scheme", back_populates="rules")
