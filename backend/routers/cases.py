import os
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

DB_PATH = "data/peekrakshak.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_cases_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            farmer_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone TEXT,
            district TEXT
        )
    """)

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(cases)")
    columns = [col[1] for col in cursor.fetchall()]
    if "farmer_id" not in columns:
        cursor.execute("ALTER TABLE cases ADD COLUMN farmer_id TEXT")
    if "farmer_name" not in columns:
        cursor.execute("ALTER TABLE cases ADD COLUMN farmer_name TEXT")
    if "severity" not in columns:
        cursor.execute("ALTER TABLE cases ADD COLUMN severity TEXT DEFAULT 'Medium'")
    if "latitude" not in columns:
        cursor.execute("ALTER TABLE cases ADD COLUMN latitude REAL")
    if "longitude" not in columns:
        cursor.execute("ALTER TABLE cases ADD COLUMN longitude REAL")
    if "image_url" not in columns:
        cursor.execute("ALTER TABLE cases ADD COLUMN image_url TEXT")

    conn.commit()
    conn.close()


init_cases_db()


@router.get("")
@router.get("/")
def list_cases():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.case_id,
            c.farmer_id,
            COALESCE(f.full_name, c.farmer_name, 'Unknown Farmer') AS farmer_name,
            c.district,
            c.crop,
            c.disease_detected,
            c.confidence,
            c.severity,
            c.latitude,
            c.longitude,
            c.image_url,
            c.status,
            c.created_at
        FROM cases c
        LEFT JOIN farmers f ON c.farmer_id = f.farmer_id
        ORDER BY c.created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    cases = []
    for row in rows:
        conf_val = row["confidence"] if row["confidence"] is not None else 0.0
        confidence_percent = round(float(conf_val) * 100) if float(conf_val) <= 1.0 else round(float(conf_val))

        raw_status = str(row["status"]).lower() if row["status"] else "pending"
        status_label = "Resolved" if "resolve" in raw_status else "Pending Expert"

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
            COALESCE(f.full_name, c.farmer_name, 'Unknown Farmer') AS farmer_name,
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
            (
                SELECT er.expert_response
                FROM expert_responses er
                WHERE er.case_id = c.case_id
                ORDER BY er.created_at DESC
                LIMIT 1
            ) AS expert_response
        FROM cases c
        LEFT JOIN farmers f ON c.farmer_id = f.farmer_id
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
        "status": row["status"],
        "expert_response": row["expert_response"],
        "created_at": row["created_at"],
    }


class ExpertResponse(BaseModel):
    expert_response: str


@router.post("/{case_id}/resolve")
def resolve_case(case_id: str, data: ExpertResponse):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT case_id FROM cases WHERE case_id = ?", (case_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found.")

    cursor.execute("""
        INSERT INTO expert_responses (case_id, expert_response)
        VALUES (?, ?)
    """, (case_id, data.expert_response))

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
        "message": "Case resolved successfully.",
        "expert_response": data.expert_response
    }