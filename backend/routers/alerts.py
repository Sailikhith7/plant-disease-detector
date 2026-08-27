from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from backend.services.alert_dispatcher import engine

router = APIRouter(prefix="/api/alerts", tags=["Outbreak Advisory Alerts"])

class OfficerBroadcastRequest(BaseModel):
    district: str
    crop: str
    disease: str
    custom_message: str

@router.get("/outbreaks")
def get_active_outbreaks(threshold: int = 5):
    """Returns list of districts where complaint count crossed threshold."""
    return engine.get_outbreak_summary(threshold=threshold)

@router.post("/broadcast")
def send_officer_broadcast(payload: OfficerBroadcastRequest):
    """Sends custom typed SMS advisory to all farmers in affected district."""
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
    import sqlite3
    conn = sqlite3.connect(engine.db_path)
    cursor = conn.cursor()
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
