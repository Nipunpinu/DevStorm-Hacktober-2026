from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.scheme import RequiredDocumentOut, ApplicationStepOut, OfficialSourceOut

class UserProfileInput(BaseModel):
    gender: Optional[str] = None
    age_group: Optional[str] = None
    marital_status: Optional[str] = None
    state: Optional[str] = None
    region_type: Optional[str] = None
    social_category: Optional[str] = None
    minority: Optional[str] = None
    disability_status: Optional[str] = None
    student_status: Optional[str] = None
    education_level: Optional[str] = None
    bpl_status: Optional[str] = None
    family_income: Optional[str] = None

class EligibilityEvaluation(BaseModel):
    status: Literal["potential_match", "does_not_match", "needs_verification"]
    status_label: str
    is_match: bool
    satisfied_conditions: List[str] = []
    violated_conditions: List[str] = []
    missing_facts: List[str] = []
    reasons: List[str] = []

class SchemeEligibilityResult(BaseModel):
    scheme_id: int
    slug: str
    name: str
    ministry: str
    category: str
    category_label: str
    is_retired: bool
    retired_details: Optional[Dict[str, Any]] = None
    numeric_benefit_value: float
    benefit_summary: str
    evaluation: EligibilityEvaluation
    documents: List[RequiredDocumentOut] = []
    steps: List[ApplicationStepOut] = []
    sources: List[OfficialSourceOut] = []
    external_portal_name: Optional[str] = None
    external_portal_url: Optional[str] = None
    verification_status: str
    last_verified_at: Optional[str] = None
    ai_report: Optional[Dict[str, Any]] = None

class EligibilityCheckRequest(BaseModel):
    profile: UserProfileInput
    language: str = Field(default="en")
    session_token: Optional[str] = None
    generate_ai_explanation: bool = Field(default=False)

class EligibilityCheckResponse(BaseModel):
    schemes: List[SchemeEligibilityResult]
    total_active: int
    total_retired: int
    evaluated_at: str
    summary_chip: str
    language: str
    privacy_notice: str = (
        "YojanaSetu adheres to DPDP privacy principles. We do not store biometric or Aadhaar numbers. "
        "Evaluations are preliminary estimates based on official departmental criteria and do not constitute legal guarantee of approval."
    )
