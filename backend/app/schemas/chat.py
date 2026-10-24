from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.eligibility import UserProfileInput

class ChatMessage(BaseModel):
    role: str = Field(description="Role: 'user', 'assistant', or 'system'")
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en")
    scheme_slug: Optional[str] = None
    conversation_history: List[ChatMessage] = []
    profile_context: Optional[UserProfileInput] = None

class ChatResponse(BaseModel):
    reply: str
    language: str
    scheme_slug: Optional[str] = None
    is_ai_generated: bool
    grounded_in_sources: List[str] = []
    disclaimer: str = (
        "Preliminary AI guidance only. Final benefit sanctions and certificate verification "
        "remain subject to competent departmental authorities."
    )
