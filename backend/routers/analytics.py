from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db, Case

router = APIRouter(tags=["Analytics"])

@router.get("/summary")
def get_summary_metrics(db: Session = Depends(get_db)):
    total = db.query(Case).count()
    pending = db.query(Case).filter(Case.status == "Pending Expert").count()
    resolved = db.query(Case).filter(Case.status == "Resolved").count()
    high_risk = db.query(Case).filter(Case.severity == "High").count()

    return {
        "total_cases": total,
        "pending_expert": pending,
        "resolved_cases": resolved,
        "high_risk_cases": high_risk
    }

@router.get("/charts")
def get_chart_data(db: Session = Depends(get_db)):
    # Disease distribution
    disease_dist = (
        db.query(Case.disease, func.count(Case.id))
        .group_by(Case.disease)
        .all()
    )

    # Risk distribution
    risk_dist = (
        db.query(Case.severity, func.count(Case.id))
        .group_by(Case.severity)
        .all()
    )

    # District distribution broken down by severity
    district_cases = (
        db.query(Case.district, Case.severity, func.count(Case.id))
        .group_by(Case.district, Case.severity)
        .all()
    )

    return {
        "disease_distribution": [{"name": d[0], "count": d[1]} for d in disease_dist],
        "risk_distribution": [{"severity": r[0], "count": r[1]} for r in risk_dist],
        "district_cases": [{"district": row[0], "severity": row[1], "count": row[2]} for row in district_cases]
    }