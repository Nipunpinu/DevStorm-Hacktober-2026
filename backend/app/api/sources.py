from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.source import OfficialSource
from backend.app.models.scheme import Scheme

router = APIRouter(prefix="/sources", tags=["Sources"])

@router.get("")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(OfficialSource).all()
    results = []
    for s in sources:
        results.append({
            "id": s.id,
            "scheme_slug": s.scheme.slug if s.scheme else None,
            "scheme_name": s.scheme.official_name if s.scheme else None,
            "source_name": s.source_name,
            "source_type": s.source_type,
            "official_url": s.official_url,
            "authority_name": s.authority_name,
            "retrieved_at": s.retrieved_at.strftime("%Y-%m-%d"),
            "last_checked_at": s.last_checked_at.strftime("%Y-%m-%d"),
            "verification_status": s.verification_status,
            "is_accessible": s.is_accessible
        })
    return results

@router.get("/summary")
def get_sources_summary(db: Session = Depends(get_db)):
    total = db.query(OfficialSource).count()
    verified = db.query(OfficialSource).filter(OfficialSource.verification_status == "verified").count()
    pending = db.query(OfficialSource).filter(OfficialSource.verification_status == "pending_review").count()
    stale = db.query(OfficialSource).filter(OfficialSource.verification_status == "stale").count()

    return {
        "total_sources": total,
        "verified_count": verified,
        "pending_review_count": pending,
        "stale_count": stale,
        "data_provenance": "All schemes link back to published Central Gazettes or statutory ministry endpoints."
    }
