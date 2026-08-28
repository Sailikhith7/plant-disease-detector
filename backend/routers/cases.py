from fastapi import APIRouter
import sqlite3

router = APIRouter(prefix="/cases", tags=["Cases"])

DB_PATH = "data/peekrakshak.db"


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

        confidence = row["confidence"]

        # Convert 0.91 → 91
        confidence_percent = round(confidence * 100)

        # Severity
        if confidence < 0.50:
            severity = "High"
        elif confidence < 0.70:
            severity = "Medium"
        else:
            severity = "Low"

        # Status
        if row["status"].lower() in [
            "open",
            "pending_expert"
        ]:
            status = "Pending Expert"
        else:
            status = "Resolved"

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

            "severity": severity,

            "status": status,

            "created_at": row["created_at"],
        })

    return {
        "status": "success",
        "cases": cases
    }