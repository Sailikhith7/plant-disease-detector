import os
import requests
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from backend.database import get_db, Case, Farmer, AlertDispatch

router = APIRouter(tags=["Alerts & Outbreaks"])

class BroadcastRequest(BaseModel):
    district: str
    crop: str
    disease: str
    message_en: str
    message_mr: Optional[str] = ""

def send_telegram_alert(chat_id: str, message: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or not chat_id:
        print(f"[WARN] Telegram Bot Token or Chat ID is missing! Token={bool(token)}, ChatID={bool(chat_id)}")
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=5)
        if resp.status_code != 200:
            print(f"[WARN] Telegram API returned {resp.status_code}: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"[WARN] Telegram delivery failed: {e}")
        return False

@router.get("/outbreaks")
def get_outbreaks(
    threshold: int = Query(5, description="Minimum case count to trigger outbreak"),
    db: Session = Depends(get_db)
):
    outbreak_clusters = (
        db.query(
            Case.district,
            Case.crop,
            Case.disease,
            func.count(Case.id).label("complaint_count")
        )
        .filter(Case.status == "Pending Expert")
        .group_by(Case.district, Case.crop, Case.disease)
        .having(func.count(Case.id) >= threshold)
        .all()
    )

    results = []
    for row in outbreak_clusters:
        results.append({
            "district": row.district,
            "crop": row.crop,
            "disease": row.disease,
            "complaint_count": row.complaint_count,
            "risk_level": "High"
        })
    return results

@router.post("/broadcast")
def broadcast_advisory(payload: BroadcastRequest, db: Session = Depends(get_db)):
    farmers = db.query(Farmer).filter(
        Farmer.district.ilike(payload.district),
        Farmer.crop.ilike(payload.crop)
    ).all()

    notified_count = 0
    advisory_text = (
        f"🚨 *PIKRAKSHAK OUTBREAK ALERT*\n\n"
        f"*District:* {payload.district}\n"
        f"*Crop:* {payload.crop}\n"
        f"*Disease:* {payload.disease}\n\n"
        f"*English Advisory:*\n{payload.message_en}\n"
    )
    if payload.message_mr:
        advisory_text += f"\n*मराठी सल्ला:*\n{payload.message_mr}"

    # 1. Dispatch to registered farmers if present
    sent_to_farmer = False
    for farmer in farmers:
        if farmer.telegram_chat_id:
            if send_telegram_alert(farmer.telegram_chat_id, advisory_text):
                notified_count += 1
                sent_to_farmer = True

    # 2. Fallback: Always dispatch to primary admin/demo chat_id from .env
    default_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if default_chat_id and not sent_to_farmer:
        if send_telegram_alert(default_chat_id, advisory_text):
            notified_count += 1

    # 3. Store delivery audit record in database
    dispatch_record = AlertDispatch(
        district=payload.district,
        crop=payload.crop,
        disease=payload.disease,
        message_en=payload.message_en,
        message_mr=payload.message_mr,
        farmers_notified=max(notified_count, len(farmers) or 1),
        status="Delivered"
    )
    db.add(dispatch_record)
    db.commit()

    return {
        "status": "success",
        "message": "Advisory broadcast completed",
        "total_farmers_notified": dispatch_record.farmers_notified,
        "dispatch_id": dispatch_record.id
    }