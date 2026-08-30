import os
import hashlib
import sqlite3
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gtts import gTTS

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

# Path relative to backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "peekrakshak.db")
DB_PATH = os.path.abspath(DB_PATH)

STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


def init_cases_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            farmer_id TEXT,
            farmer_name TEXT,
            district TEXT,
            crop TEXT,
            disease_detected TEXT,
            confidence REAL,
            severity TEXT DEFAULT 'Medium',
            latitude REAL,
            longitude REAL,
            image_url TEXT,
            status TEXT DEFAULT 'Pending Expert',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expert_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            expert_response TEXT NOT NULL,
            audio_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(expert_responses)")
    columns = [col[1] for col in cursor.fetchall()]
    if "audio_url" not in columns:
        cursor.execute("ALTER TABLE expert_responses ADD COLUMN audio_url TEXT")

    conn.commit()
    conn.close()


init_cases_db()


def generate_tts_audio(text: str, lang: str = "mr") -> str:
    try:
        clean_text = text.strip()
        if not clean_text:
            return ""
            
        text_hash = hashlib.md5(f"{clean_text}_{lang}".encode("utf-8")).hexdigest()[:12]
        audio_filename = f"prescription_{lang}_{text_hash}.mp3"
        audio_filepath = os.path.join(AUDIO_DIR, audio_filename)

        if not os.path.exists(audio_filepath):
            # Fallback to 'hi' if 'mr' has dialect pronunciation issues on gTTS
            tts_lang = "hi" if lang in ["hi", "mr"] else "en"
            tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
            tts.save(audio_filepath)

        return f"/static/audio/{audio_filename}"
    except Exception as e:
        print(f"TTS Generation failed: {e}")
        return ""


@router.get("")
@router.get("/")
def list_cases(farmer_name: Optional[str] = None, farmer_id: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT
            c.case_id,
            c.farmer_id,
            COALESCE(c.farmer_name, 'Unknown Farmer') AS farmer_name,
            c.district,
            c.crop,
            c.disease_detected,
            c.confidence,
            c.severity,
            c.latitude,
            c.longitude,
            c.image_url,
            c.status,
            c.created_at,
            er.expert_response,
            er.audio_url AS expert_audio_url
        FROM cases c
        LEFT JOIN (
            SELECT er1.case_id, er1.expert_response, er1.audio_url
            FROM expert_responses er1
            INNER JOIN (
                SELECT case_id, MAX(created_at) as max_created
                FROM expert_responses
                GROUP BY case_id
            ) er2 ON er1.case_id = er2.case_id AND er1.created_at = er2.max_created
        ) er ON c.case_id = er.case_id
        WHERE 1=1
    """
    params = []

    query += " AND COALESCE(c.farmer_name, '') NOT IN ('Unknown Farmer', '')"

    if farmer_name and farmer_name.strip():
        query += " AND LOWER(c.farmer_name) = LOWER(?)"
        params.append(farmer_name.strip())
    elif farmer_id and farmer_id.strip():
        query += " AND c.farmer_id = ?"
        params.append(farmer_id.strip())

    query += " ORDER BY c.created_at DESC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    cases = []
    for row in rows:
        conf_val = row["confidence"] if row["confidence"] is not None else 0.0
        confidence_percent = round(float(conf_val) * 100) if float(conf_val) <= 1.0 else round(float(conf_val))
        raw_status = str(row["status"]).lower() if row["status"] else "pending"
        has_expert_response = bool(row["expert_response"])
        status_label = "Resolved" if ("resolve" in raw_status or has_expert_response) else "Pending Expert"

        cases.append({
            "case_id": row["case_id"],
            "farmer_id": row["farmer_id"],
            "farmer_name": row["farmer_name"],
            "crop": row["crop"],
            "disease": row["disease_detected"],
            "confidence": confidence_percent,
            "district": row["district"],
            "severity": row["severity"] if "severity" in row.keys() and row["severity"] else "Medium",
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "image_url": row["image_url"],
            "status": status_label,
            "expert_response": row["expert_response"],
            "audio_url": row["expert_audio_url"],
            "created_at": row["created_at"],
        })

    return {
        "status": "success",
        "cases": cases
    }


@router.get("/{case_id}")
def get_case(case_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.case_id,
            c.farmer_id,
            COALESCE(c.farmer_name, 'Unknown Farmer') AS farmer_name,
            c.district,
            c.crop,
            c.disease_detected,
            c.confidence,
            c.severity,
            c.latitude,
            c.longitude,
            c.image_url,
            c.status,
            c.created_at,
            er.expert_response,
            er.audio_url AS expert_audio_url
        FROM cases c
        LEFT JOIN (
            SELECT er1.case_id, er1.expert_response, er1.audio_url
            FROM expert_responses er1
            INNER JOIN (
                SELECT case_id, MAX(created_at) as max_created
                FROM expert_responses
                GROUP BY case_id
            ) er2 ON er1.case_id = er2.case_id AND er1.created_at = er2.max_created
        ) er ON c.case_id = er.case_id
        WHERE c.case_id = ?
    """, (case_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    conf_val = row["confidence"] if row["confidence"] is not None else 0.0
    confidence_percent = round(float(conf_val) * 100) if float(conf_val) <= 1.0 else round(float(conf_val))

    raw_status = str(row["status"]).lower() if row["status"] else "pending"
    has_expert_response = bool(row["expert_response"])
    status_label = "Resolved" if ("resolve" in raw_status or has_expert_response) else "Pending Expert"

    return {
        "case_id": row["case_id"],
        "farmer_id": row["farmer_id"],
        "farmer_name": row["farmer_name"],
        "district": row["district"],
        "crop": row["crop"],
        "disease": row["disease_detected"],
        "confidence": confidence_percent,
        "severity": row["severity"] if "severity" in row.keys() and row["severity"] else "Medium",
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "image_url": row["image_url"] if "image_url" in row.keys() else None,
        "status": status_label,
        "expert_response": row["expert_response"],
        "audio_url": row["expert_audio_url"],
        "created_at": row["created_at"],
    }


class ExpertResponse(BaseModel):
    expert_response: str
    language: Optional[str] = "mr"


@router.post("/{case_id}/resolve")
def resolve_case(case_id: str, data: ExpertResponse):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT case_id FROM cases WHERE case_id = ?", (case_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found.")

    audio_url = generate_tts_audio(data.expert_response, lang=data.language or "mr")

    cursor.execute("""
        INSERT INTO expert_responses (case_id, expert_response, audio_url)
        VALUES (?, ?, ?)
    """, (case_id, data.expert_response, audio_url))

    cursor.execute("""
        UPDATE cases
        SET status = 'RESOLVED'
        WHERE case_id = ?
    """, (case_id,))

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "case_id": case_id,
        "message": "Case resolved with voice prescription.",
        "expert_response": data.expert_response,
        "audio_url": audio_url
    }