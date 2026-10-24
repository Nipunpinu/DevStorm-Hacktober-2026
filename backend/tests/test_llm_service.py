from unittest.mock import MagicMock, patch
from backend.app.services.llm_service import generate_scheme_report, generate_chat_response
from backend.app.schemas.eligibility import SchemeEligibilityResult, EligibilityEvaluation, UserProfileInput
from backend.app.schemas.scheme import RequiredDocumentOut, ApplicationStepOut, OfficialSourceOut
from datetime import datetime, timezone

def make_sample_result():
    return SchemeEligibilityResult(
        scheme_id=1,
        slug="post-matric",
        name="Post-Matric Scholarship Scheme",
        ministry="Ministry of Social Justice & Empowerment",
        category="education",
        category_label="Higher Education Grant",
        is_retired=False,
        numeric_benefit_value=48500.0,
        benefit_summary="Full fee waiver + allowance",
        evaluation=EligibilityEvaluation(
            status="potential_match",
            status_label="Preliminary Eligible",
            is_match=True,
            satisfied_conditions=["Student status verified", "Income within ceiling"],
            violated_conditions=[],
            missing_facts=[],
            reasons=["Profile matches all conditions"]
        ),
        documents=[
            RequiredDocumentOut(
                id=1, document_code="aadhaar", document_name="Aadhaar Card",
                authority="UIDAI", is_mandatory=True, steps="Download online",
                turnaround="Instant", estimated_cost="Free"
            )
        ],
        steps=[
            ApplicationStepOut(
                id=1, step_order=1, title="Register on NSP",
                description="Visit scholarships.gov.in", is_online=True
            )
        ],
        sources=[
            OfficialSourceOut(
                id=1, source_name="Gazette S.O. 123", source_type="gazette",
                official_url="https://scholarships.gov.in", authority_name="MSJE",
                retrieved_at=datetime.now(timezone.utc), last_checked_at=datetime.now(timezone.utc),
                is_accessible=True, verification_status="verified"
            )
        ],
        verification_status="verified"
    )

def test_llm_service_graceful_fallback_when_no_api_key():
    """When OpenAI API key is missing or invalid, returns deterministic report without crashing."""
    sample = make_sample_result()
    profile = UserProfileInput(student_status="Yes")
    report = generate_scheme_report(sample, profile, language="en")
    
    assert "report" in report
    rep = report["report"]
    assert rep["scheme_name"] == "Post-Matric Scholarship Scheme"
    assert rep["preliminary_status"] == "Preliminary Eligible"
    assert len(rep["conditions_satisfied"]) >= 1


def test_llm_service_with_mocked_openai():
    """Test LLM service with a mocked OpenAI response."""
    sample = make_sample_result()
    profile = UserProfileInput(student_status="Yes")

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = """
    {
        "scheme_name": "Post-Matric Scholarship Scheme",
        "preliminary_status": "Preliminary Eligible",
        "why_profile_matches_or_not": "All demographic conditions are satisfied.",
        "conditions_satisfied": ["Student status verified as Yes", "Income under 2.5L"],
        "conditions_not_satisfied": [],
        "missing_information": [],
        "benefits_summary": "Full compulsory fee waiver and 13500 living maintenance.",
        "required_documents_summary": ["Aadhaar Card"],
        "application_steps_summary": ["Step 1: Register on NSP"],
        "deadlines": "Session window closes October 31.",
        "source_and_verification_info": "Status: Verified",
        "recommended_next_steps": ["Submit form on scholarships.gov.in"],
        "disclaimer": "Standard statutory disclaimer."
    }
    """
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion

    with patch("backend.app.services.llm_service.get_openai_client", return_value=mock_client):
        res = generate_scheme_report(sample, profile, language="en")
        assert res["is_ai_available"] is True
        rep = res["report"]
        assert rep["scheme_name"] == "Post-Matric Scholarship Scheme"
        assert rep["preliminary_status"] == "Preliminary Eligible"
        assert len(rep["conditions_satisfied"]) == 2
