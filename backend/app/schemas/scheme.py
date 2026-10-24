from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class BenefitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    benefit_type: str
    amount: float
    frequency: str
    description: str
    disbursement_method: str


class RequiredDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_code: str
    document_name: str
    authority: str
    is_mandatory: bool
    top_up_benefit: Optional[str] = None
    steps: str
    turnaround: str
    estimated_cost: str
    official_guide_url: Optional[str] = None
    ready: bool = False


class ApplicationStepOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    step_order: int
    title: str
    description: str
    issuing_office: Optional[str] = None
    is_online: bool
    portal_or_form_link: Optional[str] = None


class OfficialSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    source_type: str
    official_url: str
    authority_name: str
    retrieved_at: datetime
    last_checked_at: datetime
    is_accessible: bool
    verification_status: str


class AnnouncementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str
    official_reference: Optional[str] = None
    source_url: Optional[str] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_active: bool


class SchemeTranslationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language_code: str
    localized_name: str
    localized_description: str
    localized_benefit_summary: str
    why_qualify_text: str
    why_not_qualify_text: str
    is_reviewed: bool


class SchemeDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    official_name: str
    localized_name: str
    ministry: str
    is_central: bool
    state_or_region: str
    category: str
    category_label: str
    numeric_benefit_value: float
    application_method: str
    external_portal_name: Optional[str] = None
    external_portal_url: Optional[str] = None
    status: str
    is_retired: bool
    retired_year: Optional[str] = None
    retired_reason: Optional[str] = None
    replacement_scheme_slug: Optional[str] = None
    verification_status: str
    last_verified_at: Optional[datetime] = None
    
    localized_description: str
    localized_benefit_summary: str
    why_qualify_points: List[str] = []
    why_not_qualify_points: List[str] = []
    
    benefits: List[BenefitOut] = []
    documents: List[RequiredDocumentOut] = []
    steps: List[ApplicationStepOut] = []
    sources: List[OfficialSourceOut] = []
    announcements: List[AnnouncementOut] = []
