from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.eligibility import (
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    SchemeEligibilityResult
)
from backend.app.models.user import UserProfile
from backend.app.services.eligibility import check_all_schemes_eligibility
from backend.app.services.llm_service import generate_scheme_report

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])

@router.post("/check", response_model=EligibilityCheckResponse)
def check_eligibility(
    payload: EligibilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    POST /api/eligibility/check
    Deterministic evaluation of citizen circumstances against verified government criteria.
    """
    profile = payload.profile
    lang = payload.language or "en"

    # Evaluate all schemes
    results = check_all_schemes_eligibility(db, profile, language=lang)

    # If requested and top match found, generate LLM explanatory report
    if payload.generate_ai_explanation:
        top_matches = [r for r in results if r.evaluation.status in ["potential_match", "needs_verification"] and not r.is_retired]
        if top_matches:
            top_scheme = top_matches[0]
            ai_explanation = generate_scheme_report(top_scheme, profile, language=lang)
            top_scheme.ai_report = ai_explanation.get("report")

    # Maintain anonymous user session if token provided
    if payload.session_token:
        up = db.query(UserProfile).filter(UserProfile.session_token == payload.session_token).first()
        if not up:
            up = UserProfile(
                session_token=payload.session_token,
                profile_data_json=profile.model_dump_json(),
                preferred_language=lang
            )
            db.add(up)
        else:
            up.profile_data_json = profile.model_dump_json()
            up.preferred_language = lang
            up.updated_at = datetime.now(timezone.utc)
        db.commit()

    active_count = len([r for r in results if not r.is_retired])
    retired_count = len([r for r in results if r.is_retired])

    # Summary chip text
    region = profile.region_type or "All Regions"
    category = profile.social_category or "All Categories"
    student = f"Student: {profile.student_status}" if profile.student_status else "Student: Unspecified"
    income = profile.family_income or "Income: Unspecified"
    summary_chip = f"Criteria: {region} • {category} • {student} • {income}"

    return EligibilityCheckResponse(
        schemes=results,
        total_active=active_count,
        total_retired=retired_count,
        evaluated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        summary_chip=summary_chip,
        language=lang
    )


@router.get("/options")
def get_assessment_options():
    """Returns official standardized options for demographic and economic assessment form."""
    return {
        "genders": ["Female", "Male", "Transgender", "Any / Prefer not to say"],
        "age_groups": [
            "Under 18 (School Age)",
            "18 - 25 years (Youth / Student)",
            "26 - 45 years (Working Adult)",
            "46 - 59 years (Senior Working)",
            "60+ years (Senior Citizen)"
        ],
        "marital_statuses": [
            "Single / Unmarried",
            "Married",
            "Widowed / Surviving Spouse",
            "Divorced / Separated"
        ],
        "states": [
            "All India",
            "Uttar Pradesh",
            "Maharashtra",
            "Tamil Nadu",
            "Rajasthan",
            "Madhya Pradesh",
            "Bihar",
            "West Bengal",
            "Karnataka",
            "Delhi NCT",
            "Kerala",
            "Punjab",
            "Gujarat",
            "Andhra Pradesh",
            "Odisha",
            "Assam",
            "Jammu and Kashmir"
        ],
        "region_types": [
            "Rural (Gram Panchayat / Village)",
            "Urban (Municipality / Corporation)"
        ],
        "social_categories": [
            "General / Open Category",
            "OBC (Other Backward Class)",
            "SC (Scheduled Caste)",
            "ST (Scheduled Tribe)",
            "EWS (Economically Weaker Section)"
        ],
        "minority_statuses": [
            "No",
            "Yes (Muslim, Christian, Sikh, Buddhist, Jain, Parsi)"
        ],
        "disability_statuses": [
            "None (0%)",
            "Less than 40% Disability",
            "40% or More (Benchmark Disability / UDID)"
        ],
        "student_statuses": [
            "Yes, Currently Enrolled Student",
            "No, Not Currently a Student"
        ],
        "education_levels": [
            "Class 10 or Below",
            "Higher Secondary (Class 11-12)",
            "Undergraduate / Diploma / ITI",
            "Postgraduate / Professional / PhD"
        ],
        "bpl_statuses": [
            "No (Non-BPL / APL Card)",
            "Yes (Antyodaya / BPL / Priority Ration Card)"
        ],
        "family_incomes": [
            "Below ₹1,00,000 (Low-Income EWS)",
            "₹1,00,000 - ₹2,50,000",
            "₹2,50,000 - ₹5,00,000",
            "₹5,00,000 - ₹8,00,000",
            "Above ₹8,00,000"
        ]
    }
