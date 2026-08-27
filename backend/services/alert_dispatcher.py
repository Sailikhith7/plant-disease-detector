import os
import requests
import json
import logging
import sqlite3
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertEngine")

class OutbreakAlertEngine:
    def __init__(self, db_path: str = "data/peekrakshak.db", bot_token: str = "8899516372:AAG7vxg5nZHGavPKSHI3uyIrpOTUA9yoyII"):
        self.db_path = db_path
        self.bot_token = bot_token
        self.telegram_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Farmers Directory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id TEXT UNIQUE,
                full_name TEXT,
                phone_number TEXT,
                district TEXT,
                taluka TEXT,
                primary_crop TEXT,
                telegram_chat_id TEXT
            )
        ''')

        # Disease Case / Complaint Reports Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE,
                district TEXT,
                crop TEXT,
                disease_detected TEXT,
                confidence REAL,
                status TEXT DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Broadcast Dispatches Audit Trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_dispatches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT,
                crop TEXT,
                disease TEXT,
                target_phone TEXT,
                officer_message TEXT,
                delivery_channel TEXT,
                status TEXT,
                dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Auto-migration if column 'crop' is missing in existing sqlite table
        cursor.execute("PRAGMA table_info(alert_dispatches)")
        columns = [col[1] for col in cursor.fetchall()]
        if "crop" not in columns:
            cursor.execute("ALTER TABLE alert_dispatches ADD COLUMN crop TEXT")
        if "officer_message" not in columns:
            cursor.execute("ALTER TABLE alert_dispatches ADD COLUMN officer_message TEXT")

        # Seed sample farmers if empty
        cursor.execute("SELECT COUNT(*) FROM farmers")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO farmers (farmer_id, full_name, phone_number, district, taluka, primary_crop, telegram_chat_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [
                ('MH_YAV_001', 'Ramesh Patil', '7710974749', 'Yavatmal', 'Pusad', 'Cotton', '7696303650'),
                ('MH_YAV_002', 'Suresh Deshmukh', '9811122233', 'Yavatmal', 'Darwha', 'Cotton', '7696303650'),
                ('MH_NAN_001', 'Kishore Jadhav', '9844455566', 'Nanded', 'Hadgaon', 'Soybean', '7696303650'),
                ('MH_NAS_001', 'Sunil Shinde', '9833344455', 'Nashik', 'Niphad', 'Tomato', '7696303650')
            ])

        # Seed 6 complaints for Yavatmal Cotton Pink Bollworm (>5 threshold)
        cursor.execute("SELECT COUNT(*) FROM cases")
        if cursor.fetchone()[0] == 0:
            mock_cases = [
                (f'CASE_YAV_{i}', 'Yavatmal', 'Cotton', 'pink_bollworm', 0.94) for i in range(1, 7)
            ]
            cursor.executemany('''
                INSERT INTO cases (case_id, district, crop, disease_detected, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', mock_cases)

        conn.commit()
        conn.close()

    def get_outbreak_summary(self, threshold: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT district, crop, disease_detected, COUNT(*) as case_count
            FROM cases
            WHERE status = 'OPEN'
            GROUP BY district, crop, disease_detected
            HAVING case_count >= ?
        ''', (threshold,))
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "district": r[0],
                "crop": r[1],
                "disease": r[2],
                "case_count": r[3],
                "threshold_breached": True
            }
            for r in rows
        ]

    def get_target_farmers(self, district: str, crop: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT farmer_id, full_name, phone_number, telegram_chat_id 
            FROM farmers 
            WHERE district = ? AND primary_crop = ?
        ''', (district, crop))
        rows = cursor.fetchall()
        conn.close()
        return [{"farmer_id": r[0], "name": r[1], "phone": r[2], "chat_id": r[3]} for r in rows]

    def dispatch_custom_officer_broadcast(self, district: str, crop: str, disease: str, custom_message: str) -> Dict:
        farmers = self.get_target_farmers(district, crop)
        if not farmers:
            return {"status": "skipped", "message": f"No farmers registered for {district} - {crop}"}

        dispatches = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for farmer in farmers:
            formatted_sms = (
                f"🚨 *[कृषी विभाग चेतावणी अलर्ट - {district}]*\n\n"
                f"शेतकरी बांधव: *{farmer['name']}*\n"
                f"पीक: *{crop}* | रोग: *{disease}*\n\n"
                f"📢 *कृषी अधिकाऱ्यांचा संदेश:*\n{custom_message}\n\n"
                f"🏛 _तातडीच्या मदतीसाठी तालुका कृषी कार्यालयाशी संपर्क साधावा._"
            )

            delivery_status = "DELIVERED"
            try:
                res = requests.post(self.telegram_url, json={
                    "chat_id": farmer["chat_id"],
                    "text": formatted_sms,
                    "parse_mode": "Markdown"
                }, timeout=8)
                if not res.json().get("ok"):
                    delivery_status = "LOGGED"
            except Exception:
                delivery_status = "LOGGED"

            cursor.execute('''
                INSERT INTO alert_dispatches (district, crop, disease, target_phone, officer_message, delivery_channel, status)
                VALUES (?, ?, ?, ?, ?, 'telegram/sms', ?)
            ''', (district, crop, disease, farmer["phone"], custom_message, delivery_status))

            dispatches.append({"farmer_name": farmer["name"], "phone": farmer["phone"], "status": delivery_status})

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "district": district,
            "crop": crop,
            "disease": disease,
            "total_farmers_notified": len(dispatches),
            "dispatches": dispatches
        }

engine = OutbreakAlertEngine()
