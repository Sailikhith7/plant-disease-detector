import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db, Case

router = APIRouter(tags=["Cases"])

class ResolveCaseRequest(BaseModel):
    expert_diagnosis: str
    prescription: str

@router.get("/cases")
def get_cases(
    status: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    crop: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    if district:
        query = query.filter(Case.district.ilike(f"%{district}%"))
    if crop:
        query = query.filter(Case.crop.ilike(f"%{crop}%"))
    if severity:
        query = query.filter(Case.severity == severity)
    
    return query.order_by(Case.created_at.desc()).all()

@router.get("/cases/{case_id}")
def get_case_detail(case_id: int, db: Session = Depends(get_db)):
    case_obj = db.query(Case).filter(Case.id == case_id).first()
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
    return case_obj

@router.post("/cases/{case_id}/resolve")
def resolve_case(case_id: int, payload: ResolveCaseRequest, db: Session = Depends(get_db)):
    case_obj = db.query(Case).filter(Case.id == case_id).first()
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_obj.status = "Resolved"
    case_obj.expert_diagnosis = payload.expert_diagnosis
    case_obj.prescription = payload.prescription
    case_obj.resolved_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(case_obj)
    return {"status": "success", "message": "Case resolved successfully", "case": case_obj}