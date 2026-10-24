from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.scheme import Scheme
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.llm_service import generate_chat_response
from backend.app.services.translation_service import get_scheme_localized

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    POST /api/assistant/chat
    Answers user queries with real SQL records grounded in verified departmental guidelines.
    """
    scheme_context = None
    if payload.scheme_slug:
        scheme = db.query(Scheme).filter(Scheme.slug == payload.scheme_slug).first()
        if scheme:
            loc = get_scheme_localized(db, scheme.id, payload.language)
            scheme_context = {
                "name": loc["name"] or scheme.official_name,
                "ministry": scheme.ministry,
                "benefit_summary": loc["benefit_summary"],
                "criteria": "; ".join([r.description for r in scheme.rules]),
                "documents": ", ".join([d.document_name for d in scheme.documents]),
                "external_portal_name": scheme.external_portal_name or "Official Portal",
                "external_portal_url": scheme.external_portal_url or "",
                "verification_status": scheme.verification_status,
                "sources": [src.source_name for src in scheme.sources]
            }

    conv_history = [
        {"role": m.role, "content": m.content}
        for m in payload.conversation_history
    ]

    result = generate_chat_response(
        message=payload.message,
        language=payload.language,
        scheme_context=scheme_context,
        profile=payload.profile_context,
        conversation_history=conv_history
    )

    return ChatResponse(
        reply=result["reply"],
        language=payload.language,
        scheme_slug=payload.scheme_slug,
        is_ai_generated=result.get("is_ai_generated", False),
        grounded_in_sources=result.get("grounded_in_sources", []),
        provider=result.get("provider", "huggingface")
    )


@router.get("/test-hf")
def test_huggingface_connection():
    """
    GET /api/assistant/test-hf
    Safe diagnostic verification of Hugging Face Inference Providers connection.
    Tests connectivity without exposing tokens or personal citizen data.
    """
    from backend.app.services.llm_service import test_hf_connection
    return test_hf_connection()
