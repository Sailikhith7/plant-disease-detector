from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

DB_PATH = "data/peekrakshak.db"


# =========================================================
# GET ALL CASES
# =========================================================

@router.get("/")
def list_cases():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.case_id,
            c.farmer_id,
            f.full_name AS farmer_name,
            c.district,
            c.crop,
            c.disease_detected,
            c.confidence,
            c.status,
            c.created_at
        FROM cases c
        LEFT JOIN farmers f
            ON c.farmer_id = f.farmer_id
        ORDER BY c.created_at DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    cases = []

    for row in rows:

        confidence = float(row["confidence"])
        confidence_percent = round(confidence * 100)

        cases.append({
            "case_id": row["case_id"],
            "farmer_id": row["farmer_id"],
            "farmer_name": (
                row["farmer_name"]
                if row["farmer_name"]
                else "Unknown Farmer"
            ),
            "crop": row["crop"],
            "disease": row["disease_detected"],
            "confidence": confidence_percent,
            "district": row["district"],
            "status": (
                "Pending Expert"
                if row["status"].lower()
                in ["open", "pending_expert"]
                else "Resolved"
            ),
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

    # Make sure the expert response table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expert_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            expert_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        SELECT
            c.case_id,
            c.farmer_id,
            f.full_name AS farmer_name,
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
        LEFT JOIN farmers f
            ON c.farmer_id = f.farmer_id
        WHERE c.case_id = ?
    """, (case_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    return {
        "case_id": row["case_id"],
        "farmer_id": row["farmer_id"],
        "farmer_name": row["farmer_name"],
        "district": row["district"],
        "crop": row["crop"],
        "disease": row["disease_detected"],
        "confidence": round(
            float(row["confidence"]) * 100
        ),
        "status": row["status"],
        "expert_response": row["expert_response"],
        "created_at": row["created_at"],
    }


# =========================================================
# EXPERT RESPONSE MODEL
# =========================================================

class ExpertResponse(BaseModel):
    expert_response: str


# =========================================================
# EXPERT RESOLVES CASE
# =========================================================

@router.post("/{case_id}/resolve")
def resolve_case(
    case_id: str,
    data: ExpertResponse
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # -----------------------------------------------------
    # Check whether case exists
    # -----------------------------------------------------

    cursor.execute(
        "SELECT case_id FROM cases WHERE case_id = ?",
        (case_id,)
    )

    case = cursor.fetchone()

    if case is None:

        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    # -----------------------------------------------------
    # Create expert response table if it doesn't exist
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expert_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            expert_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # Save expert response
    # -----------------------------------------------------

    cursor.execute("""
        INSERT INTO expert_responses (
            case_id,
            expert_response
        )
        VALUES (?, ?)
    """, (
        case_id,
        data.expert_response
    ))

    # -----------------------------------------------------
    # Mark case as resolved
    # -----------------------------------------------------

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

