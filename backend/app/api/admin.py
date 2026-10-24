import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.admin import AdminAccount, AdminAuditLog
from backend.app.models.scheme import Scheme, SchemeTranslation, RequiredDocument, ApplicationStep
from backend.app.models.source import OfficialSource, SourceVerificationHistory
from backend.app.schemas.admin import (
    AdminLoginRequest,
    TokenResponse,
    AdminOut,
    AdminCreate,
    SchemeCreateAdmin,
    SchemeUpdateAdmin,
    SourceVerificationRequest,
    AuditLogOut
)
from backend.app.security.auth import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_admin,
    require_role
)
from backend.app.services.source_service import import_schemes_from_json, import_schemes_from_csv, check_stale_records

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(AdminAccount).filter(
        (AdminAccount.username == payload.username_or_email) |
        (AdminAccount.email == payload.username_or_email)
    ).first()

    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrative username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative account is deactivated"
        )

    admin.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(data={"sub": admin.username, "role": admin.role})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=admin.role,
        username=admin.username
    )


@router.get("/me", response_model=AdminOut)
def get_current_admin_profile(current_admin: AdminAccount = Depends(get_current_admin)):
    return current_admin


@router.get("/verification-queue")
def get_verification_queue(
    current_admin: AdminAccount = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lists schemes and sources pending administrative verification or stale."""
    pending_schemes = db.query(Scheme).filter(
        (Scheme.verification_status == "pending_review") | (Scheme.status == "pending_review")
    ).all()

    pending_sources = db.query(OfficialSource).filter(
        OfficialSource.verification_status == "pending_review"
    ).all()

    stale_sources = check_stale_records(db)

    return {
        "pending_schemes": [
            {
                "id": s.id,
                "slug": s.slug,
                "name": s.official_name,
                "ministry": s.ministry,
                "status": s.status,
                "verification_status": s.verification_status,
                "created_at": s.created_at.strftime("%Y-%m-%d")
            } for s in pending_schemes
        ],
        "pending_sources": [
            {
                "id": src.id,
                "scheme_slug": src.scheme.slug if src.scheme else None,
                "source_name": src.source_name,
                "official_url": src.official_url,
                "status": src.verification_status
            } for src in pending_sources
        ],
        "stale_sources": stale_sources
    }


@router.post("/verify-source")
def verify_source(
    payload: SourceVerificationRequest,
    current_admin: AdminAccount = Depends(require_role(["superadmin", "reviewer"])),
    db: Session = Depends(get_db)
):
    source = db.query(OfficialSource).filter(OfficialSource.id == payload.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    old_status = source.verification_status
    source.verification_status = payload.new_status
    source.last_checked_at = datetime.now(timezone.utc)
    source.notes = payload.notes

    # Add verification history
    history = SourceVerificationHistory(
        source_id=source.id,
        checked_at=datetime.now(timezone.utc),
        status_code=source.http_status,
        change_detected=old_status != payload.new_status,
        notes=payload.notes or f"Status updated from {old_status} to {payload.new_status}",
        verified_by_admin=current_admin.username
    )
    db.add(history)

    # If all sources of scheme are verified, update scheme verification status
    if source.scheme:
        all_sources = source.scheme.sources
        if all(s.verification_status == "verified" for s in all_sources):
            source.scheme.verification_status = "verified"
            source.scheme.last_verified_at = datetime.now(timezone.utc)

    # Log to audit log
    audit = AdminAuditLog(
        admin_id=current_admin.id,
        action="verify_source",
        target_entity="official_sources",
        target_entity_id=str(source.id),
        details_json=json.dumps({"old_status": old_status, "new_status": payload.new_status, "notes": payload.notes})
    )
    db.add(audit)
    db.commit()

    return {"success": True, "source_id": source.id, "new_status": source.verification_status}


@router.post("/schemes/publish/{slug}")
def publish_scheme(
    slug: str,
    current_admin: AdminAccount = Depends(require_role(["superadmin", "reviewer"])),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.slug == slug).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    scheme.status = "active"
    scheme.verification_status = "verified"
    scheme.last_verified_at = datetime.now(timezone.utc)

    audit = AdminAuditLog(
        admin_id=current_admin.id,
        action="publish_scheme",
        target_entity="schemes",
        target_entity_id=scheme.slug,
        details_json=json.dumps({"name": scheme.official_name, "status": "active"})
    )
    db.add(audit)
    db.commit()

    return {"success": True, "slug": scheme.slug, "status": scheme.status}


@router.post("/schemes/withdraw/{slug}")
def withdraw_scheme(
    slug: str,
    reason: str = "Administrative policy sunset or gazette revocation",
    current_admin: AdminAccount = Depends(require_role(["superadmin", "reviewer"])),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.slug == slug).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    scheme.status = "withdrawn"
    scheme.is_retired = True
    scheme.retired_reason = reason
    scheme.retired_year = str(datetime.now(timezone.utc).year)

    audit = AdminAuditLog(
        admin_id=current_admin.id,
        action="withdraw_scheme",
        target_entity="schemes",
        target_entity_id=scheme.slug,
        details_json=json.dumps({"reason": reason})
    )
    db.add(audit)
    db.commit()

    return {"success": True, "slug": scheme.slug, "status": scheme.status}


@router.post("/import/json")
def import_json_schemes(
    schemes_data: List[Dict[str, Any]],
    current_admin: AdminAccount = Depends(require_role(["superadmin", "reviewer"])),
    db: Session = Depends(get_db)
):
    res = import_schemes_from_json(db, schemes_data, admin_id=current_admin.id)
    return res


@router.post("/import/csv")
async def import_csv_schemes(
    file: UploadFile = File(...),
    current_admin: AdminAccount = Depends(require_role(["superadmin", "reviewer"])),
    db: Session = Depends(get_db)
):
    content = await file.read()
    csv_text = content.decode("utf-8")
    res = import_schemes_from_csv(db, csv_text, admin_id=current_admin.id)
    return res


@router.get("/audit-logs", response_model=List[AuditLogOut])
def view_audit_logs(
    limit: int = 50,
    current_admin: AdminAccount = Depends(require_role(["superadmin", "auditor"])),
    db: Session = Depends(get_db)
):
    logs = db.query(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit).all()
    return logs
