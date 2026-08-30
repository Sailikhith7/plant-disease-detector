import os
import hashlib
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from gtts import gTTS

from backend.database import get_db, Case, Farmer, ExpertResponse, Base, engine

# Ensure tables are created on whichever DB DATABASE_URL points to
Base.metadata.create_all(bind=engine)

# Dynamically ensure audio_url column exists in expert_responses if using SQLite/Postgres
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE expert_responses ADD COLUMN IF NOT EXISTS audio_url VARCHAR"))
        conn.commit()
except Exception:
    pass

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


def _confidence_percent(conf_val):
    conf_val = conf_val if conf_val is not None else 0.0
    conf_val = float(conf_val)
    return round(conf_val * 100) if conf_val <= 1.0 else round(conf_val)


def _status_label(raw_status, has_response=False):
    raw_status = str(raw_status).lower() if raw_status else "pending"
    return "Resolved" if ("resolve" in raw_status or has_response) else "Pending Expert"


def generate_tts_audio(text_content: str, lang: str = "mr") -> str:
    try:
        clean_text = text_content.strip()
        if not clean_text:
            return ""

        text_hash = hashlib.md5(f"{clean_text}_{lang}".encode("utf-8")).hexdigest()[:12]
        audio_filename = f"prescription_{lang}_{text_hash}.mp3"
        audio_filepath = os.path.join(AUDIO_DIR, audio_filename)

        if not os.path.exists(audio_filepath):
            tts_lang = "hi" if lang in ["hi", "mr"] else "en"
            tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
            tts.save(audio_filepath)

        return f"/static/audio/{audio_filename}"
    except Exception as e:
        print(f"TTS Generation failed: {e}")
        return ""


@router.get("")
@router.get("/")
def list_cases(
    farmer_name: Optional[str] = None,
    farmer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(Case, Farmer)
        .outerjoin(Farmer, Case.farmer_id == Farmer.farmer_id)
        .order_by(desc(Case.created_at))
    )

    if farmer_name and farmer_name.strip():
        search_name = f"%{farmer_name.strip()}%"
        query = query.filter(
            (Case.farmer_name.ilike(search_name)) | (Farmer.name.ilike(search_name))
        )
    elif farmer_id and farmer_id.strip():
        query = query.filter(Case.farmer_id == farmer_id.strip())

    rows = query.all()
    cases = []

    for case, farmer in rows:
        resolved_farmer_name = (
            farmer.name if farmer and farmer.name
            else (case.farmer_name or "Unknown Farmer")
        )

        # Exclude unknown / blank records
        if resolved_farmer_name in ["Unknown Farmer", ""]:
            continue

        latest_resp = (
            db.query(ExpertResponse)
            .filter(ExpertResponse.case_id == case.case_id)
            .order_by(desc(ExpertResponse.created_at))
            .first()
        )

        cases.append({
            "case_id": case.case_id,
            "farmer_id": case.farmer_id,
            "farmer_name": resolved_farmer_name,
            "crop": case.crop,
            "disease": case.disease_detected,
            "confidence": _confidence_percent(case.confidence),
            "district": case.district,
            "severity": case.severity or "Medium",
            "latitude": case.latitude,
            "longitude": case.longitude,
            "image_url": case.image_url,
            "status": _status_label(case.status, has_response=bool(latest_resp)),
            "expert_response": latest_resp.expert_response if latest_resp else None,
            "audio_url": getattr(latest_resp, "audio_url", None) if latest_resp else None,
            "created_at": str(case.created_at) if case.created_at else None,
        })

    return {
        "status": "success",
        "cases": cases
    }


@router.get("/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    result = (
        db.query(Case, Farmer)
        .outerjoin(Farmer, Case.farmer_id == Farmer.farmer_id)
        .filter(Case.case_id == case_id)
        .first()
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    case, farmer = result
    resolved_farmer_name = (
        farmer.name if farmer and farmer.name
        else (case.farmer_name or "Unknown Farmer")
    )

    latest_response = (
        db.query(ExpertResponse)
        .filter(ExpertResponse.case_id == case_id)
        .order_by(desc(ExpertResponse.created_at))
        .first()
    )

    return {
        "case_id": case.case_id,
        "farmer_id": case.farmer_id,
        "farmer_name": resolved_farmer_name,
        "district": case.district,
        "crop": case.crop,
        "disease": case.disease_detected,
        "confidence": _confidence_percent(case.confidence),
        "severity": case.severity or "Medium",
        "latitude": case.latitude,
        "longitude": case.longitude,
        "image_url": case.image_url,
        "status": _status_label(case.status, has_response=bool(latest_response)),
        "expert_response": latest_response.expert_response if latest_response else None,
        "audio_url": getattr(latest_response, "audio_url", None) if latest_response else None,
        "created_at": str(case.created_at) if case.created_at else None,
    }


class ExpertResponseIn(BaseModel):
    expert_response: str
    language: Optional[str] = "mr"


@router.post("/{case_id}/resolve")
def resolve_case(case_id: str, data: ExpertResponseIn, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    audio_url = generate_tts_audio(data.expert_response, lang=data.language or "mr")

    new_response = ExpertResponse(
        case_id=case_id,
        expert_response=data.expert_response
    )
    if hasattr(new_response, "audio_url"):
        setattr(new_response, "audio_url", audio_url)

    db.add(new_response)
    case.status = "RESOLVED"
    db.commit()

    return {
        "status": "success",
        "case_id": case_id,
        "message": "Case resolved with voice prescription.",
        "expert_response": data.expert_response,
        "audio_url": audio_url
    }