from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.scheme import Scheme, SchemeTranslation

def search_schemes(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    is_retired: Optional[bool] = False,
    sort_by: str = "benefit_desc"
) -> List[Scheme]:
    """
    Retrieves schemes from SQL with category filter, query match, and sorting.
    """
    stmt = db.query(Scheme)

    if is_retired is not None:
        stmt = stmt.filter(Scheme.is_retired == is_retired)

    if category and category.lower() != "all":
        stmt = stmt.filter(Scheme.category == category.lower())

    if query and query.strip():
        q_wild = f"%{query.strip()}%"
        stmt = stmt.outerjoin(SchemeTranslation).filter(
            or_(
                Scheme.official_name.ilike(q_wild),
                Scheme.ministry.ilike(q_wild),
                Scheme.category.ilike(q_wild),
                SchemeTranslation.localized_name.ilike(q_wild),
                SchemeTranslation.localized_description.ilike(q_wild)
            )
        ).distinct()

    if sort_by == "benefit_desc":
        stmt = stmt.order_by(Scheme.numeric_benefit_value.desc())
    elif sort_by == "benefit_asc":
        stmt = stmt.order_by(Scheme.numeric_benefit_value.asc())
    elif sort_by == "name_asc":
        stmt = stmt.order_by(Scheme.official_name.asc())
    else:
        stmt = stmt.order_by(Scheme.numeric_benefit_value.desc())

    return stmt.all()
