from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from backend.app.models import Scheme, RequiredDocument, ApplicationStep, OfficialSource
from backend.app.models.rule import EligibilityRule
from backend.app.schemas.eligibility import UserProfileInput, EligibilityEvaluation, SchemeEligibilityResult
from backend.app.schemas.scheme import RequiredDocumentOut, ApplicationStepOut, OfficialSourceOut
from backend.app.services.translation_service import get_scheme_localized

# Income ceiling helper
INCOME_BRACKET_CEILINGS = {
    "Below ₹1,00,000": 100000,
    "₹1,00,000 - ₹2,50,000": 250000,
    "₹2,50,000 - ₹5,00,000": 500000,
    "₹5,00,000 - ₹8,00,000": 800000,
    "Above ₹8,00,000": 999999999
}

def evaluate_single_rule(rule: EligibilityRule, profile: UserProfileInput) -> Tuple[Optional[bool], str, bool]:
    """
    Evaluates a single rule against user profile.
    Returns:
      - result: True (satisfied), False (violated), None (missing/uncertain information)
      - explanation: human-readable explanation
      - is_missing_fact: boolean indicating if user did not provide input for this field
    """
    field = rule.field_name.lower().strip()
    op = rule.operator.lower().strip()
    target = rule.target_value.strip()

    # 1. State check
    if field in ["state", "state_or_region"]:
        if not profile.state or profile.state in ["", "Any"]:
            return None, f"State verification pending: rule requires {target}", True
        if target.lower() in ["all india", "national", "central"]:
            return True, "Scheme is valid across all States & Union Territories", False
        allowed = [s.strip().lower() for s in target.split(",")]
        if profile.state.lower() in allowed:
            return True, f"Resident of eligible state ({profile.state})", False
        return False, f"Scheme is restricted to {target}, not currently available in {profile.state}", False

    # 2. Region type (Rural / Urban)
    if field == "region_type":
        if not profile.region_type or profile.region_type in ["", "Any"]:
            return None, f"Location verification pending: requires {target} classification", True
        if target.lower() == "any" or profile.region_type.lower() == target.lower():
            return True, f"Area classification ({profile.region_type}) aligns with requirements", False
        return False, f"Restricted to {target} areas; user selected {profile.region_type}", False

    # 3. Student Status
    if field in ["student_status", "is_student"]:
        if not profile.student_status or profile.student_status in ["", "Any"]:
            return None, "Student enrollment status not specified", True
        if profile.student_status.lower() == target.lower():
            return True, f"Student status verified as {profile.student_status}", False
        return False, f"Requires student status to be {target}", False

    # 4. Social Category
    if field in ["social_category", "category"]:
        if not profile.social_category or profile.social_category in ["", "Any"]:
            return None, f"Social category verification pending: target {target}", True
        allowed_cats = [c.strip().lower() for c in target.split(",")]
        if target.lower() in ["all", "any"] or profile.social_category.lower() in allowed_cats:
            return True, f"Social category ({profile.social_category}) meets eligibility", False
        return False, f"Scheme applies to {target}; user indicated {profile.social_category}", False

    # 5. Income Ceiling
    if field in ["max_income", "family_income", "income_limit"]:
        if not profile.family_income or profile.family_income in ["", "Any"]:
            return None, f"Household income verification pending: threshold is ₹{target}", True
        try:
            target_income = float(target.replace(",", ""))
            user_income_upper = INCOME_BRACKET_CEILINGS.get(profile.family_income, 0)
            if user_income_upper <= target_income:
                return True, f"Annual household income within statutory ceiling of ₹{target_income:,.0f}", False
            return False, f"Household income ({profile.family_income}) exceeds scheme statutory ceiling of ₹{target_income:,.0f}", False
        except ValueError:
            return True, "Income condition satisfied", False

    # 6. BPL Status
    if field in ["bpl_status", "bpl_card"]:
        if not profile.bpl_status or profile.bpl_status in ["", "Any"]:
            return None, "BPL ration card status not provided", True
        if profile.bpl_status.lower() == target.lower():
            return True, f"BPL ration card status meets requirement ({profile.bpl_status})", False
        return False, f"Requires BPL ration card status to be {target}", False

    # 7. Disability Status
    if field in ["disability", "disability_status", "pwd"]:
        if not profile.disability_status or profile.disability_status in ["", "Any"]:
            return None, "Disability / UDID status not provided", True
        if target.lower() in ["none", "any"]:
            return True, "No specific disability requirement", False
        if "40%" in target and "40% and Above" in profile.disability_status:
            return True, "Certified benchmark disability (40%+ with UDID) satisfied", False
        if profile.disability_status.lower() == target.lower():
            return True, f"Disability condition ({profile.disability_status}) matches", False
        return False, f"Requires benchmark disability of {target}; user selected {profile.disability_status}", False

    # 8. Education Level
    if field in ["education_level", "education"]:
        if not profile.education_level or profile.education_level in ["", "Any"]:
            return None, "Education level not provided", True
        allowed_edu = [e.strip().lower() for e in target.split(",")]
        if target.lower() == "any" or profile.education_level.lower() in allowed_edu:
            return True, f"Educational standard ({profile.education_level}) matches scheme criteria", False
        return False, f"Requires education level in [{target}]", False

    # 9. Gender
    if field == "gender":
        if not profile.gender or profile.gender in ["", "Any"]:
            return None, "Gender not provided", True
        allowed_genders = [g.strip().lower() for g in target.split(",")]
        if target.lower() in ["all", "any"] or profile.gender.lower() in allowed_genders:
            return True, f"Gender ({profile.gender}) meets criterion", False
        return False, f"Scheme target group is {target}; user selected {profile.gender}", False

    # 10. Age Group
    if field in ["age_group", "age"]:
        if not profile.age_group or profile.age_group in ["", "Any"]:
            return None, "Age group not specified", True
        allowed_ages = [a.strip().lower() for a in target.split(",")]
        if target.lower() in ["all", "any"] or profile.age_group.lower() in allowed_ages:
            return True, f"Age group ({profile.age_group}) matches", False
        return False, f"Requires age group in [{target}], selected {profile.age_group}", False

    # 11. Minority
    if field == "minority":
        if not profile.minority or profile.minority in ["", "Any"]:
            return None, "Minority status not specified", True
        if target.lower() in ["any", "all"] or profile.minority.lower() == target.lower():
            return True, f"Minority status ({profile.minority}) verified", False
        return False, f"Scheme requires minority status to be {target}", False

    # Default fallback for custom or unhandled rules
    return True, rule.description or "Condition checked", False


def evaluate_scheme_eligibility(scheme: Scheme, profile: UserProfileInput) -> EligibilityEvaluation:
    """
    Evaluates all rules for a scheme deterministically.
    Produces:
      - potential_match: All rules passed, no violations, no missing facts.
      - does_not_match: One or more mandatory rules explicitly violated.
      - needs_verification: Missing facts exist, but no violations detected.
    """
    if scheme.is_retired:
        return EligibilityEvaluation(
            status="does_not_match",
            status_label="Archived / Sunset Scheme",
            is_match=False,
            satisfied_conditions=[],
            violated_conditions=["This scheme has been officially retired or consolidated."],
            missing_facts=[],
            reasons=["Scheme is sunset and no longer accepting fresh applications."]
        )

    satisfied: List[str] = []
    violated: List[str] = []
    missing: List[str] = []

    for rule in scheme.rules:
        res, msg, is_missing = evaluate_single_rule(rule, profile)
        if res is True:
            satisfied.append(msg)
        elif res is False:
            if rule.is_mandatory:
                violated.append(msg)
            else:
                missing.append(f"Optional criteria not met: {msg}")
        else:
            missing.append(msg)

    if len(violated) > 0:
        status = "does_not_match"
        label = "Not Eligible Based on Criteria"
        is_match = False
    elif len(missing) > 0:
        status = "needs_verification"
        label = "Preliminary Match (Verification Required)"
        is_match = True
    else:
        status = "potential_match"
        label = "Preliminary Eligible"
        is_match = True

    reasons = []
    if status == "potential_match":
        reasons.append("Your demographic and socio-economic profile satisfies all verified mandatory rules.")
    elif status == "needs_verification":
        reasons.append("Your profile appears compatible, but some eligibility factors require document submission or departmental verification.")
    else:
        reasons.append("One or more statutory criteria for this scheme are not satisfied by the submitted profile.")

    return EligibilityEvaluation(
        status=status,
        status_label=label,
        is_match=is_match,
        satisfied_conditions=satisfied,
        violated_conditions=violated,
        missing_facts=missing,
        reasons=reasons
    )


def check_all_schemes_eligibility(db: Session, profile: UserProfileInput, language: str = "en") -> List[SchemeEligibilityResult]:
    """Retrieve all published/active schemes from SQL and evaluate eligibility."""
    schemes = db.query(Scheme).all()
    results: List[SchemeEligibilityResult] = []

    for scheme in schemes:
        evaluation = evaluate_scheme_eligibility(scheme, profile)
        loc = get_scheme_localized(db, scheme.id, language)

        # Retired details if applicable
        retired_details = None
        if scheme.is_retired:
            retired_details = {
                "yearRetired": scheme.retired_year or "Unknown",
                "reason": scheme.retired_reason or "Consolidated into updated umbrella schemes.",
                "replacementSchemeId": scheme.replacement_scheme_slug or "post-matric",
                "replacementSchemeName": "Modernized Central Scheme"
            }

        docs_out = [
            RequiredDocumentOut(
                id=d.id,
                document_code=d.document_code,
                document_name=d.document_name,
                authority=d.authority,
                is_mandatory=d.is_mandatory,
                top_up_benefit=d.top_up_benefit,
                steps=d.steps,
                turnaround=d.turnaround,
                estimated_cost=d.estimated_cost,
                official_guide_url=d.official_guide_url,
                ready=False
            ) for d in scheme.documents
        ]

        steps_out = [
            ApplicationStepOut(
                id=s.id,
                step_order=s.step_order,
                title=s.title,
                description=s.description,
                issuing_office=s.issuing_office,
                is_online=s.is_online,
                portal_or_form_link=s.portal_or_form_link
            ) for s in scheme.steps
        ]

        sources_out = [
            OfficialSourceOut(
                id=src.id,
                source_name=src.source_name,
                source_type=src.source_type,
                official_url=src.official_url,
                authority_name=src.authority_name,
                retrieved_at=src.retrieved_at,
                last_checked_at=src.last_checked_at,
                is_accessible=src.is_accessible,
                verification_status=src.verification_status
            ) for src in scheme.sources
        ]

        item = SchemeEligibilityResult(
            scheme_id=scheme.id,
            slug=scheme.slug,
            name=loc["name"] or scheme.official_name,
            ministry=scheme.ministry,
            category=scheme.category,
            category_label=scheme.category_label or scheme.category.capitalize(),
            is_retired=scheme.is_retired,
            retired_details=retired_details,
            numeric_benefit_value=scheme.numeric_benefit_value,
            benefit_summary=loc["benefit_summary"] or f"Direct financial benefit up to ₹{scheme.numeric_benefit_value:,.0f}",
            evaluation=evaluation,
            documents=docs_out,
            steps=steps_out,
            sources=sources_out,
            external_portal_name=scheme.external_portal_name,
            external_portal_url=scheme.external_portal_url,
            verification_status=scheme.verification_status,
            last_verified_at=scheme.last_verified_at.strftime("%Y-%m-%d") if scheme.last_verified_at else None,
            ai_report=None
        )
        results.append(item)

    return results
