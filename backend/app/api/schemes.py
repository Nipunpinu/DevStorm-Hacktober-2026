from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.scheme import Scheme, RequiredDocument
from backend.app.schemas.scheme import SchemeDetail, RequiredDocumentOut
from backend.app.services.scheme_search import search_schemes
from backend.app.services.translation_service import get_scheme_localized

router = APIRouter(prefix="/schemes", tags=["Schemes"])

@router.get("")
def list_schemes(
    category: Optional[str] = Query(None, description="education, farmers, livelihood, disability, all"),
    is_retired: Optional[bool] = Query(False, description="Filter retired schemes"),
    query: Optional[str] = Query(None, description="Search keyword"),
    sort_by: str = Query("benefit_desc", description="benefit_desc, benefit_asc, name_asc"),
    lang: str = Query("en", description="Language code"),
    db: Session = Depends(get_db)
):
    schemes = search_schemes(db, query=query, category=category, is_retired=is_retired, sort_by=sort_by)
    output = []
    for s in schemes:
        loc = get_scheme_localized(db, s.id, lang)
        output.append({
            "id": s.id,
            "slug": s.slug,
            "official_name": s.official_name,
            "localized_name": loc["name"] or s.official_name,
            "ministry": s.ministry,
            "category": s.category,
            "category_label": s.category_label,
            "numeric_benefit_value": s.numeric_benefit_value,
            "benefit_summary": loc["benefit_summary"] or f"Up to ₹{s.numeric_benefit_value:,.0f}",
            "is_retired": s.is_retired,
            "retired_year": s.retired_year,
            "retired_reason": s.retired_reason,
            "replacement_scheme_slug": s.replacement_scheme_slug,
            "verification_status": s.verification_status,
            "last_verified_at": s.last_verified_at.strftime("%Y-%m-%d") if s.last_verified_at else None,
            "documents_count": len(s.documents),
            "mandatory_docs_count": len([d for d in s.documents if d.is_mandatory]),
            "steps_count": len(s.steps),
            "why_qualify": loc["why_qualify"],
            "why_not_qualify": loc["why_not_qualify"]
        })
    return output


@router.get("/{slug}")
def get_scheme_detail(
    slug: str,
    lang: str = Query("en"),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.slug == slug).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    loc = get_scheme_localized(db, scheme.id, lang)
    
    return {
        "id": scheme.id,
        "slug": scheme.slug,
        "official_name": scheme.official_name,
        "localized_name": loc["name"] or scheme.official_name,
        "ministry": scheme.ministry,
        "is_central": scheme.is_central,
        "state_or_region": scheme.state_or_region,
        "category": scheme.category,
        "category_label": scheme.category_label,
        "numeric_benefit_value": scheme.numeric_benefit_value,
        "application_method": scheme.application_method,
        "external_portal_name": scheme.external_portal_name,
        "external_portal_url": scheme.external_portal_url,
        "status": scheme.status,
        "is_retired": scheme.is_retired,
        "retired_year": scheme.retired_year,
        "retired_reason": scheme.retired_reason,
        "replacement_scheme_slug": scheme.replacement_scheme_slug,
        "verification_status": scheme.verification_status,
        "last_verified_at": scheme.last_verified_at.strftime("%Y-%m-%d") if scheme.last_verified_at else None,
        "localized_description": loc["description"],
        "localized_benefit_summary": loc["benefit_summary"],
        "why_qualify_points": loc["why_qualify"],
        "why_not_qualify_points": loc["why_not_qualify"],
        "documents": [
            {
                "id": d.id,
                "document_code": d.document_code,
                "document_name": d.document_name,
                "authority": d.authority,
                "is_mandatory": d.is_mandatory,
                "top_up_benefit": d.top_up_benefit,
                "steps": d.steps,
                "turnaround": d.turnaround,
                "estimated_cost": d.estimated_cost,
                "official_guide_url": d.official_guide_url,
                "ready": False
            } for d in scheme.documents
        ],
        "steps": [
            {
                "id": st.id,
                "step_order": st.step_order,
                "title": st.title,
                "description": st.description,
                "issuing_office": st.issuing_office,
                "is_online": st.is_online,
                "portal_or_form_link": st.portal_or_form_link
            } for st in scheme.steps
        ],
        "sources": [
            {
                "id": src.id,
                "source_name": src.source_name,
                "source_type": src.source_type,
                "official_url": src.official_url,
                "authority_name": src.authority_name,
                "verification_status": src.verification_status
            } for src in scheme.sources
        ]
    }


@router.get("/{slug}/checklist")
def get_scheme_checklist(
    slug: str,
    lang: str = Query("en"),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.slug == slug).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    loc = get_scheme_localized(db, scheme.id, lang)
    docs = scheme.documents

    mandatory = [
        {
            "id": d.id,
            "document_code": d.document_code,
            "document_name": d.document_name,
            "authority": d.authority,
            "is_mandatory": True,
            "steps": d.steps,
            "turnaround": d.turnaround,
            "estimated_cost": d.estimated_cost,
            "official_guide_url": d.official_guide_url,
            "ready": False
        } for d in docs if d.is_mandatory
    ]

    optional = [
        {
            "id": d.id,
            "document_code": d.document_code,
            "document_name": d.document_name,
            "authority": d.authority,
            "is_mandatory": False,
            "top_up_benefit": d.top_up_benefit,
            "steps": d.steps,
            "turnaround": d.turnaround,
            "estimated_cost": d.estimated_cost,
            "official_guide_url": d.official_guide_url,
            "ready": False
        } for d in docs if not d.is_mandatory
    ]

    return {
        "scheme_slug": scheme.slug,
        "scheme_name": loc["name"] or scheme.official_name,
        "mandatory_documents": mandatory,
        "optional_documents": optional,
        "total_mandatory": len(mandatory),
        "total_optional": len(optional)
    }
