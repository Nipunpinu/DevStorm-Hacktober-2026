from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.services.llm_service import (
    get_hf_client,
    generate_chat_response,
    generate_scheme_report,
    test_hf_connection as execute_test_hf_connection,
    LANGUAGE_NAME_MAP,
    LANGUAGE_OFFLINE_MESSAGES
)
from backend.app.schemas.eligibility import SchemeEligibilityResult, EligibilityEvaluation, UserProfileInput
from backend.app.schemas.scheme import RequiredDocumentOut, ApplicationStepOut, OfficialSourceOut
from datetime import datetime, timezone

client = TestClient(app)


def make_dummy_scheme():
    return SchemeEligibilityResult(
        scheme_id=2,
        slug="pm-surya",
        name="PM Surya Ghar: Muft Bijli Yojana",
        ministry="Ministry of New and Renewable Energy",
        category="livelihood",
        category_label="Clean Energy & Capital Subsidy",
        is_retired=False,
        numeric_benefit_value=78000.0,
        benefit_summary="Capital cash subsidy up to ₹78,000 for residential 3kW rooftop solar",
        evaluation=EligibilityEvaluation(
            status="potential_match",
            status_label="Preliminary Match",
            is_match=True,
            satisfied_conditions=["Residential roof ownership verified", "Domestic electricity connection"],
            violated_conditions=[],
            missing_facts=[],
            reasons=["All conditions met"]
        ),
        documents=[
            RequiredDocumentOut(
                id=1, document_code="electricity_bill", document_name="Recent Electricity Bill",
                authority="State DISCOM", is_mandatory=True, steps="Download from utility portal",
                turnaround="Instant", estimated_cost="Free"
            )
        ],
        steps=[
            ApplicationStepOut(
                id=1, step_order=1, title="Register on National Portal",
                description="pmsuryaghar.gov.in", is_online=True
            )
        ],
        sources=[
            OfficialSourceOut(
                id=1, source_name="Gazette Notification 2024", source_type="gazette",
                official_url="https://pmsuryaghar.gov.in", authority_name="MNRE",
                retrieved_at=datetime.now(timezone.utc), last_checked_at=datetime.now(timezone.utc),
                is_accessible=True, verification_status="verified"
            )
        ],
        verification_status="verified"
    )


def test_hf_client_initialization():
    """Verify InferenceClient initialization with token and provider settings."""
    with patch.object(settings, "HF_TOKEN", "hf_mock_token_1234567890"), \
         patch.object(settings, "HF_PROVIDER", "together"):
        hf_client = get_hf_client()
        assert hf_client is not None
        assert hf_client.token == "hf_mock_token_1234567890"


def test_hf_chat_completion_success():
    """Verify Hugging Face InferenceClient chat completions return grounded response."""
    mock_hf_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Under PM Surya Ghar, eligible households receive up to ₹78,000 direct subsidy."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_hf_client.chat.completions.create.return_value = mock_response

    scheme_context = {
        "name": "PM Surya Ghar: Muft Bijli Yojana",
        "ministry": "MNRE",
        "benefit_summary": "Subsidy up to ₹78,000",
        "criteria": "Residential roof ownership",
        "documents": "Electricity bill",
        "external_portal_name": "National Portal",
        "external_portal_url": "https://pmsuryaghar.gov.in",
        "verification_status": "verified",
        "sources": ["Gazette Notification 2024"]
    }

    with patch("backend.app.services.llm_service.get_hf_client", return_value=mock_hf_client):
        result = generate_chat_response(
            message="What is the benefit under PM Surya Ghar?",
            language="en",
            scheme_context=scheme_context,
            profile=None,
            conversation_history=[]
        )

        assert result["is_ai_generated"] is True
        assert result["provider"] == "huggingface"
        assert "78,000" in result["reply"]
        assert len(result["grounded_in_sources"]) == 1


def test_hf_error_handling_401_auth_failure():
    """Verify 401 Unauthorized returns helpful authentication notice without crashing."""
    mock_hf_client = MagicMock()
    mock_hf_client.chat.completions.create.side_effect = Exception("HfHubHTTPError 401 Client Error: Unauthorized for url")

    with patch("backend.app.services.llm_service.get_hf_client", return_value=mock_hf_client):
        result = generate_chat_response(
            message="Tell me about PM Surya Ghar",
            language="en",
            scheme_context={"name": "PM Surya Ghar"},
            profile=None,
            conversation_history=[]
        )

        assert result["is_ai_generated"] is False
        assert result["provider"] == "huggingface_fallback"
        assert "Authentication Error" in result["reply"]
        assert "HF_TOKEN" in result["reply"]


def test_hf_error_handling_402_payment_required():
    """Verify 402 Payment Required returns clear billing guidance and preserves database facts."""
    mock_hf_client = MagicMock()
    mock_hf_client.chat.completions.create.side_effect = Exception("HfHubHTTPError Client error '402 Payment Required' for url")

    with patch("backend.app.services.llm_service.get_hf_client", return_value=mock_hf_client):
        result = generate_chat_response(
            message="Tell me about PM Surya Ghar",
            language="en",
            scheme_context={"name": "PM Surya Ghar"},
            profile=None,
            conversation_history=[]
        )

        assert result["is_ai_generated"] is False
        assert result["provider"] == "huggingface_fallback"
        assert "billing" in result["reply"].lower() or "credits" in result["reply"].lower()


def test_hf_error_handling_429_rate_limit():
    """Verify 429 Rate Limit error returns retry advisory."""
    mock_hf_client = MagicMock()
    mock_hf_client.chat.completions.create.side_effect = Exception("HfHubHTTPError 429 Client Error: Rate limit reached")

    with patch("backend.app.services.llm_service.get_hf_client", return_value=mock_hf_client):
        result = generate_chat_response(
            message="Tell me about PM Surya Ghar",
            language="en",
            scheme_context={"name": "PM Surya Ghar"},
            profile=None,
            conversation_history=[]
        )

        assert result["is_ai_generated"] is False
        assert "Rate Limit" in result["reply"]


def test_hf_error_handling_model_not_supported():
    """Verify BadRequestError for unsupported model/provider returns informative notice."""
    mock_hf_client = MagicMock()
    mock_hf_client.chat.completions.create.side_effect = Exception("BadRequestError: model is not supported by any provider enabled")

    with patch("backend.app.services.llm_service.get_hf_client", return_value=mock_hf_client):
        result = generate_chat_response(
            message="Tell me about PM Surya Ghar",
            language="en",
            scheme_context={"name": "PM Surya Ghar"},
            profile=None,
            conversation_history=[]
        )

        assert result["is_ai_generated"] is False
        assert "not supported" in result["reply"].lower() or "notice" in result["reply"].lower()


def test_hf_multi_language_prompts():
    """Verify all 14 official Indian languages have metadata mapping and offline fallbacks."""
    expected_languages = [
        "en", "hi", "mr", "bn", "te", "ta", "ml", "gu", "pa", "kn", "or", "as", "ur", "sa", "ks"
    ]
    for lang in expected_languages:
        assert lang in LANGUAGE_NAME_MAP, f"Language {lang} missing in LANGUAGE_NAME_MAP"
        assert lang in LANGUAGE_OFFLINE_MESSAGES, f"Language {lang} missing in LANGUAGE_OFFLINE_MESSAGES"
        msg = LANGUAGE_OFFLINE_MESSAGES[lang].format(scheme_name="Test Scheme")
        assert len(msg) > 10


def test_hf_deterministic_rule_integrity_preserved():
    """Verify LLM cannot overturn deterministic eligibility status."""
    sample = make_dummy_scheme()
    sample.evaluation.status_label = "Preliminary Match"
    profile = UserProfileInput(student_status="No")

    mock_hf_client = MagicMock()
    mock_choice = MagicMock()
    # Mock LLM trying to return "Approved" or overturn status
    mock_choice.message.content = """
    {
        "scheme_name": "PM Surya Ghar",
        "preliminary_status": "Officially Approved and Sanctioned",
        "why_profile_matches_or_not": "Matches criteria.",
        "conditions_satisfied": ["Ownership confirmed"],
        "conditions_not_satisfied": [],
        "missing_information": [],
        "benefits_summary": "Up to ₹78,000",
        "required_documents_summary": ["Electricity Bill"],
        "application_steps_summary": ["Apply online"],
        "deadlines": "None",
        "source_and_verification_info": "Verified",
        "recommended_next_steps": ["Proceed to portal"],
        "disclaimer": "Official legal disclaimer."
    }
    """
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_hf_client.chat.completions.create.return_value = mock_response

    with patch("backend.app.services.llm_service.get_hf_client", return_value=mock_hf_client):
        res = generate_scheme_report(sample, profile, language="en")
        assert res["is_ai_available"] is True
        # Preliminary status MUST be preserved from the deterministic rules engine
        assert res["report"]["preliminary_status"] == "Preliminary Match"


def test_safe_diagnostic_endpoint():
    """Verify GET /api/assistant/test-hf diagnostic endpoint never exposes secret tokens."""
    res = client.get("/api/assistant/test-hf")
    assert res.status_code == 200
    data = res.json()
    assert "configured" in data
    assert "status" in data
    assert "model" in data
    assert "provider" in data
    
    # Critical security assertion: full token is NEVER returned
    raw_token = settings.effective_hf_token
    if raw_token:
        assert raw_token not in str(data), "CRITICAL: Secret token leaked in API response!"
    if "token_masked" in data:
        assert data["token_masked"].startswith("hf_") or data["token_masked"] == "***"
        assert len(data["token_masked"]) < 16, "Masked token must obscure secret keys"


def test_api_assistant_chat_endpoint_integration():
    """Verify POST /api/assistant/chat responds with proper provider and grounded sources."""
    res = client.post("/api/assistant/chat", json={
        "message": "What documents do I need for solar rooftop scheme?",
        "language": "en",
        "scheme_slug": "pm-surya"
    })
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert "provider" in data
    assert len(data["reply"]) > 10
    # No secret leaked
    raw_token = settings.effective_hf_token
    if raw_token:
        assert raw_token not in data["reply"]
