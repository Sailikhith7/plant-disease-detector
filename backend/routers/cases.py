import os
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

# Use unified database path (creates directory if missing)
DB_PATH = "data/peekrakshak.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_cases_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure farmers table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            farmer_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone TEXT,
            district TEXT
        )
    """)

    # Ensure cases table exists with all required columns
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

    # Ensure expert responses table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expert_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            expert_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Schema migration: Ensure farmer_id exists if an older table was created
    cursor.execute("PRAGMA table_info(cases)")
    columns = [col[1] for col in cursor.fetchall()]
    if "farmer_id" not in columns:
        cursor.execute("ALTER TABLE cases ADD COLUMN farmer_id TEXT")
    if "farmer_name" not in columns:
        cursor.execute("ALTER TABLE cases ADD COLUMN farmer_name TEXT")

    conn.commit()
    conn.close()


# Initialize database tables on load
init_cases_db()


# =========================================================
# GET ALL CASES (Supports both /api/cases and /api/cases/)
# =========================================================

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
            "status": status_label,
            "created_at": row["created_at"],
        })

    return {
        "status": "success",
        "cases": cases
    }


# =========================================================
# GET SINGLE CASE
# =========================================================

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
        "status": row["status"],
        "expert_response": row["expert_response"],
        "created_at": row["created_at"],
    }


# =========================================================
# EXPERT RESPONSE MODEL & RESOLUTION
# =========================================================

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