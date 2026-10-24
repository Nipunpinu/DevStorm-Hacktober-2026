from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class AdminLoginRequest(BaseModel):
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class AdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    role: str = Field(default="reviewer")

class SchemeCreateAdmin(BaseModel):
    slug: str
    official_name: str
    ministry: str
    is_central: bool = True
    state_or_region: str = "All India"
    category: str
    category_label: str
    numeric_benefit_value: float = 0.0
    application_method: str = "online"
    external_portal_name: Optional[str] = None
    external_portal_url: Optional[str] = None
    status: str = "pending_review"
    verification_status: str = "pending_review"

class SchemeUpdateAdmin(BaseModel):
    official_name: Optional[str] = None
    ministry: Optional[str] = None
    is_central: Optional[bool] = None
    state_or_region: Optional[str] = None
    category: Optional[str] = None
    category_label: Optional[str] = None
    numeric_benefit_value: Optional[float] = None
    application_method: Optional[str] = None
    external_portal_name: Optional[str] = None
    external_portal_url: Optional[str] = None
    status: Optional[str] = None
    verification_status: Optional[str] = None

class SourceVerificationRequest(BaseModel):
    source_id: int
    new_status: str = Field(..., description="verified, pending_review, stale, broken")
    notes: Optional[str] = None

class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: Optional[int]
    action: str
    target_entity: str
    target_entity_id: Optional[str]
    details_json: str
    ip_address: Optional[str]
    created_at: datetime
