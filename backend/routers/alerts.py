import os
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from backend.services.alert_dispatcher import engine

router = APIRouter(tags=["Alerts & Outbreaks"])

DB_PATH = "data/peekrakshak.db"


class OfficerBroadcastRequest(BaseModel):
    district: str
    crop: str
    disease: str
    custom_message: str


@router.get("/outbreaks")
def get_active_outbreaks(threshold: int = 5):
    """Returns list of districts where complaint count crossed threshold."""
    # 1. Try engine first
    try:
        engine_res = engine.get_outbreak_summary(threshold=threshold)
        if engine_res and (isinstance(engine_res, list) and len(engine_res) > 0 or (isinstance(engine_res, dict) and engine_res.get("outbreaks"))):
            return engine_res
    except Exception:
        pass

    # 2. Direct fallback from cases table
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            district, 
            crop, 
            disease_detected AS disease, 
            COUNT(*) as case_count
        FROM cases
        GROUP BY district, crop, disease_detected
        HAVING COUNT(*) >= ?
    """, (threshold,))

    rows = cursor.fetchall()
    conn.close()

    outbreaks = []
    for r in rows:
        outbreaks.append({
            "district": r["district"],
            "crop": r["crop"],
            "disease": r["disease"],
            "case_count": r["case_count"],
            "threshold_breached": True,
            "risk": "High",
            "severity": "High"
        })

    return outbreaks


@router.post("/broadcast")
def send_officer_broadcast(payload: OfficerBroadcastRequest):
    """Sends Telegram and SMS advisory to farmers in affected district."""
    if not payload.custom_message.strip():
        raise HTTPException(status_code=400, detail="Officer custom message cannot be empty.")
    
    result = engine.dispatch_custom_officer_broadcast(
        district=payload.district,
        crop=payload.crop,
        disease=payload.disease,
        custom_message=payload.custom_message
    )
    return result


@router.get("/history")
def get_broadcast_logs():
    """Returns dispatch audit logs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_dispatches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT,
            crop TEXT,
            disease TEXT,
            target_phone TEXT,
            officer_message TEXT,
            status TEXT,
            dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute('''
        SELECT id, district, crop, disease, target_phone, officer_message, status, dispatched_at 
        FROM alert_dispatches 
        ORDER BY dispatched_at DESC LIMIT 50
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "district": r[1], "crop": r[2], "disease": r[3],
            "phone": r[4], "message": r[5], "status": r[6], "timestamp": r[7]
        }
        for r in rows
    ]