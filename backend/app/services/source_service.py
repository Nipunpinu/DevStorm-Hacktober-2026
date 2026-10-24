import csv
import io
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
import httpx

from backend.app.models.scheme import Scheme, SchemeTranslation, Benefit, RequiredDocument, ApplicationStep
from backend.app.models.source import OfficialSource, SourceVerificationHistory
from backend.app.models.rule import EligibilityRule
from backend.app.models.admin import AdminAuditLog

logger = logging.getLogger(__name__)

async def verify_source_accessibility(source_url: str) -> Tuple[bool, int, str]:
    """
    Checks if an official portal or gazette URL is accessible with timeout & security checks.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # Send HEAD or GET request
            response = await client.head(source_url)
            if response.status_code == 405: # Method not allowed, try GET
                response = await client.get(source_url)
            is_ok = 200 <= response.status_code < 400
            return is_ok, response.status_code, f"Status code: {response.status_code}"
    except httpx.TimeoutException:
        return False, 504, "Connection timed out"
    except Exception as e:
        return False, 500, f"Accessibility check error: {str(e)[:150]}"


def check_stale_records(db: Session, max_days: int = 90) -> List[Dict[str, Any]]:
    """Identifies sources not verified in the last `max_days` days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    stale_sources = db.query(OfficialSource).filter(
        OfficialSource.last_checked_at < cutoff
    ).all()
    
    results = []
    for s in stale_sources:
        results.append({
            "source_id": s.id,
            "scheme_slug": s.scheme.slug if s.scheme else "unknown",
            "source_name": s.source_name,
            "official_url": s.official_url,
            "last_checked": s.last_checked_at.strftime("%Y-%m-%d"),
            "status": "stale"
        })
    return results


def import_schemes_from_json(db: Session, data: List[Dict[str, Any]], admin_id: int) -> Dict[str, Any]:
    """
    Imports scheme records from JSON with duplicate detection, validation, and review queue.
    """
    created_count = 0
    updated_count = 0
    errors: List[str] = []

    for item in data:
        slug = item.get("slug", "").strip()
        if not slug:
            errors.append("Skipping record with missing slug")
            continue

        existing = db.query(Scheme).filter(Scheme.slug == slug).first()
        is_update = existing is not None

        scheme = existing or Scheme(slug=slug)
        scheme.official_name = item.get("official_name", slug)
        scheme.ministry = item.get("ministry", "Unspecified Ministry")
        scheme.is_central = item.get("is_central", True)
        scheme.state_or_region = item.get("state_or_region", "All India")
        scheme.category = item.get("category", "livelihood")
        scheme.category_label = item.get("category_label", scheme.category.capitalize())
        scheme.numeric_benefit_value = float(item.get("numeric_benefit_value", 0.0))
        scheme.application_method = item.get("application_method", "online")
        scheme.external_portal_name = item.get("external_portal_name")
        scheme.external_portal_url = item.get("external_portal_url")
        scheme.status = item.get("status", "pending_review")
        scheme.is_retired = item.get("is_retired", False)
        scheme.retired_year = item.get("retired_year")
        scheme.retired_reason = item.get("retired_reason")
        scheme.replacement_scheme_slug = item.get("replacement_scheme_slug")
        scheme.verification_status = "pending_review"  # New imports require admin verification

        if not is_update:
            db.add(scheme)
            db.flush()
            created_count += 1
        else:
            updated_count += 1

        # Translations
        translations_data = item.get("translations", [])
        for trans in translations_data:
            lang_code = trans.get("language_code", "en")
            st = db.query(SchemeTranslation).filter(
                SchemeTranslation.scheme_id == scheme.id,
                SchemeTranslation.language_code == lang_code
            ).first()
            if not st:
                st = SchemeTranslation(scheme_id=scheme.id, language_code=lang_code)
                db.add(st)
            st.localized_name = trans.get("localized_name", scheme.official_name)
            st.localized_description = trans.get("localized_description", "")
            st.localized_benefit_summary = trans.get("localized_benefit_summary", "")
            st.why_qualify_text = trans.get("why_qualify_text", "")
            st.why_not_qualify_text = trans.get("why_not_qualify_text", "")
            st.is_reviewed = trans.get("is_reviewed", False)

        # Rules
        rules_data = item.get("rules", [])
        if rules_data and is_update:
            db.query(EligibilityRule).filter(EligibilityRule.scheme_id == scheme.id).delete()
        for r in rules_data:
            rule = EligibilityRule(
                scheme_id=scheme.id,
                rule_code=r.get("rule_code", "rule"),
                field_name=r.get("field_name", ""),
                operator=r.get("operator", "eq"),
                target_value=str(r.get("target_value", "")),
                is_mandatory=r.get("is_mandatory", True),
                description=r.get("description", ""),
                failure_reason=r.get("failure_reason", "")
            )
            db.add(rule)

        # Documents
        docs_data = item.get("documents", [])
        if docs_data and is_update:
            db.query(RequiredDocument).filter(RequiredDocument.scheme_id == scheme.id).delete()
        for d in docs_data:
            doc = RequiredDocument(
                scheme_id=scheme.id,
                document_code=d.get("document_code", "doc"),
                document_name=d.get("document_name", "Document"),
                authority=d.get("authority", "Official Authority"),
                is_mandatory=d.get("is_mandatory", True),
                top_up_benefit=d.get("top_up_benefit"),
                steps=d.get("steps", "Submit at counter or portal"),
                turnaround=d.get("turnaround", "3 - 7 Days"),
                estimated_cost=d.get("estimated_cost", "Free"),
                official_guide_url=d.get("official_guide_url")
            )
            db.add(doc)

        # Application steps
        steps_data = item.get("steps", [])
        if steps_data and is_update:
            db.query(ApplicationStep).filter(ApplicationStep.scheme_id == scheme.id).delete()
        for s in steps_data:
            step = ApplicationStep(
                scheme_id=scheme.id,
                step_order=s.get("step_order", 1),
                title=s.get("title", ""),
                description=s.get("description", ""),
                issuing_office=s.get("issuing_office"),
                is_online=s.get("is_online", True),
                portal_or_form_link=s.get("portal_or_form_link")
            )
            db.add(step)

        # Official sources
        sources_data = item.get("sources", [])
        for src in sources_data:
            existing_src = db.query(OfficialSource).filter(
                OfficialSource.scheme_id == scheme.id,
                OfficialSource.official_url == src.get("official_url")
            ).first()
            if not existing_src:
                new_src = OfficialSource(
                    scheme_id=scheme.id,
                    source_name=src.get("source_name", "Official Gazette"),
                    source_type=src.get("source_type", "gazette"),
                    official_url=src.get("official_url", "https://india.gov.in"),
                    authority_name=src.get("authority_name", scheme.ministry),
                    verification_status="pending_review"
                )
                db.add(new_src)

    # Log action to audit log
    audit_entry = AdminAuditLog(
        admin_id=admin_id,
        action="import_schemes_json",
        target_entity="schemes",
        details_json=json.dumps({
            "created": created_count,
            "updated": updated_count,
            "errors": errors
        })
    )
    db.add(audit_entry)
    db.commit()

    return {
        "success": True,
        "created_count": created_count,
        "updated_count": updated_count,
        "errors": errors
    }


def import_schemes_from_csv(db: Session, csv_content: str, admin_id: int) -> Dict[str, Any]:
    """
    Parses a CSV file of schemes, validates rows, and queues for admin verification.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    created = 0
    updated = 0
    errors = []

    for row in reader:
        slug = row.get("slug", "").strip()
        if not slug:
            errors.append("CSV row missing 'slug' column")
            continue

        existing = db.query(Scheme).filter(Scheme.slug == slug).first()
        scheme = existing or Scheme(slug=slug)

        scheme.official_name = row.get("official_name", slug)
        scheme.ministry = row.get("ministry", "Central Ministry")
        scheme.is_central = row.get("is_central", "true").lower() in ["true", "1", "yes"]
        scheme.state_or_region = row.get("state_or_region", "All India")
        scheme.category = row.get("category", "education")
        scheme.numeric_benefit_value = float(row.get("numeric_benefit_value", 0.0) or 0.0)
        scheme.application_method = row.get("application_method", "online")
        scheme.external_portal_name = row.get("external_portal_name")
        scheme.external_portal_url = row.get("external_portal_url")
        scheme.status = "pending_review"
        scheme.verification_status = "pending_review"

        if not existing:
            db.add(scheme)
            created += 1
        else:
            updated += 1

    db.commit()
    return {"success": True, "created": created, "updated": updated, "errors": errors}
