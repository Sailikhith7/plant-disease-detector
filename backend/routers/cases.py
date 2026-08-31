from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from backend.database import get_db, Case, Farmer, ExpertResponse, Base, engine

# Make sure tables exist on whichever DB DATABASE_URL points to (Neon in prod,
# local sqlite in dev). This is idempotent (CREATE TABLE IF NOT EXISTS-style).
Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)


def _confidence_percent(conf_val):
    conf_val = conf_val if conf_val is not None else 0.0
    conf_val = float(conf_val)
    return round(conf_val * 100) if conf_val <= 1.0 else round(conf_val)


def _status_label(raw_status):
    raw_status = str(raw_status).lower() if raw_status else "pending"
    return "Resolved" if "resolve" in raw_status else "Pending Expert"


@router.get("")
@router.get("/")
def list_cases(db: Session = Depends(get_db)):

    rows = (
        db.query(Case)
        .order_by(desc(Case.created_at))
        .all()
    )

    cases = []

    for case in rows:

        cases.append({
            "case_id": case.case_id,
            "farmer_id": case.farmer_id,

            "farmer_name": (
                case.farmer_name
                or "Unknown Farmer"
            ),

            "crop": case.crop,

            "disease": case.disease_detected,

            "confidence": _confidence_percent(
                case.confidence
            ),

            "district": case.district,

            "severity": (
                case.severity
                or "Medium"
            ),

            "latitude": case.latitude,

            "longitude": case.longitude,

            "image_url": case.image_url,

            "status": _status_label(
                case.status
            ),

            "created_at": case.created_at,
        })

    return {
        "status": "success",
        "cases": cases
    }


@router.get("/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db)
):

    case = (
        db.query(Case)
        .filter(Case.case_id == case_id)
        .first()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    latest_response = (
        db.query(ExpertResponse)
        .filter(
            ExpertResponse.case_id == case_id
        )
        .order_by(
            desc(ExpertResponse.created_at)
        )
        .first()
    )

    return {
        "case_id": case.case_id,

        "farmer_id": case.farmer_id,

        "farmer_name": (
            case.farmer_name
            or "Unknown Farmer"
        ),

        "district": case.district,

        "crop": case.crop,

        "disease": case.disease_detected,

        "confidence": _confidence_percent(
            case.confidence
        ),

        "severity": (
            case.severity
            or "Medium"
        ),

        "latitude": case.latitude,

        "longitude": case.longitude,

        "image_url": case.image_url,

        "status": case.status,

        "expert_response": (
            latest_response.expert_response
            if latest_response
            else None
        ),

        "created_at": case.created_at,
    }

class ExpertResponseIn(BaseModel):
    expert_response: str


class ExpertRequestIn(BaseModel):
    reason: str
    description: Optional[str] = None


@router.post("/{case_id}/expert-request")
def request_expert_review(
    case_id: str,
    data: ExpertRequestIn,
    db: Session = Depends(get_db)
):
    case = (
        db.query(Case)
        .filter(Case.case_id == case_id)
        .first()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    case.status = "PENDING_EXPERT"

    db.commit()
    db.refresh(case)

    return {
        "status": "success",
        "case_id": case_id,
        "message": "Expert review requested successfully.",
        "reason": data.reason,
        "description": data.description
    }

@router.post("/{case_id}/resolve")
def resolve_case(case_id: str, data: ExpertResponseIn, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    db.add(ExpertResponse(case_id=case_id, expert_response=data.expert_response))
    case.status = "RESOLVED"

    db.commit()

    return {
        "status": "success",
        "case_id": case_id,
        "message": "Case resolved successfully.",
        "expert_response": data.expert_response
    }