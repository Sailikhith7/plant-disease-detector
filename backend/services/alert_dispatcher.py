import os
import json
import logging
import sqlite3
from typing import Dict, List, Optional
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OutbreakAlertEngine")

DISEASE_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    "pink_bollworm": {
        "crop": "Cotton",
        "marathi_name": "गुलाबी बोंडअळी (Pink Bollworm)",
        "default_remedy": "फेरोमोन ट्रॅप एकरी ५ लावा आणि निंबोळी अर्क ५% किंवा प्रोफिनोफॉस ५०% EC (३० मिली/१० लिटर) फवारणी करा."
    },
    "soybean_rust": {
        "crop": "Soybean",
        "marathi_name": "सोयाबीन तांबेरा (Soybean Rust)",
        "default_remedy": "हेक्साकोनाझोल ५% EC (१० मिली) किंवा टेब्युकोनाझोल (१० मिली/१० लिटर) पाण्यात मिसळून तात्काळ फवारणी करा."
    },
    "leaf_curl": {
        "crop": "Tomato",
        "marathi_name": "पाने आकसणे/कुरळे रोग (Leaf Curl)",
        "default_remedy": "पांढऱ्या माशीच्या नियंत्रणासाठी डायमेथोएट ३०% EC (१५ मिली/१० लिटर) फवारणी करावी."
    }
}

class OutbreakAlertEngine:
    def __init__(self, db_path: str = "data/peekrakshak.db", bot_token: str = "8899516372:AAG7vxg5nZHGavPKSHI3uyIrpOTUA9yoyII"):
        self.db_path = db_path
        self.bot_token = bot_token
        self.telegram_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self._init_sqlite_mock_db()

    def _init_sqlite_mock_db(self):
        """Initializes local SQLite database with schema and mock farmers if not exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Farmers registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id TEXT UNIQUE,
                full_name TEXT,
                phone_number TEXT,
                district TEXT,
                taluka TEXT,
                primary_crop TEXT,
                preferred_lang TEXT DEFAULT 'mr',
                telegram_chat_id TEXT
            )
        ''')

        # Disease scan logs (to detect outbreaks)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT,
                district TEXT,
                crop TEXT,
                disease_detected TEXT,
                confidence REAL,
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Alert dispatch history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_dispatches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT,
                disease TEXT,
                target_phone TEXT,
                message_body TEXT,
                delivery_channel TEXT,
                status TEXT,
                dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Seed initial farmer dataset if empty
        cursor.execute("SELECT COUNT(*) FROM farmers")
        if cursor.fetchone()[0] == 0:
            mock_farmers = [
                ('MH_YAV_001', 'Ramesh Patil', '7710974749', 'Yavatmal', 'Pusad', 'Cotton', 'mr', '7696303650'),
                ('MH_YAV_002', 'Suresh Deshmukh', '9811122233', 'Yavatmal', 'Darwha', 'Cotton', 'mr', '7696303650'),
                ('MH_NAN_001', 'Kishore Jadhav', '9844455566', 'Nanded', 'Hadgaon', 'Soybean', 'mr', '7696303650'),
                ('MH_NAS_001', 'Sunil Shinde', '9833344455', 'Nashik', 'Niphad', 'Tomato', 'mr', '7696303650')
            ]
            cursor.executemany('''
                INSERT INTO farmers (farmer_id, full_name, phone_number, district, taluka, primary_crop, preferred_lang, telegram_chat_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', mock_farmers)

        conn.commit()
        conn.close()

    def check_outbreak_threshold(self, district: str, disease_key: str, threshold: int = 3) -> bool:
        """Evaluates scan records to detect cluster outbreaks in a district."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM disease_scans 
            WHERE district = ? AND disease_detected = ?
        ''', (district, disease_key))
        count = cursor.fetchone()[0]
        conn.close()
        return count >= threshold

    def get_target_farmers(self, district: str, crop: str) -> List[Dict]:
        """Fetches registered farmers in affected zone cultivating the specific crop."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT farmer_id, full_name, phone_number, district, taluka, telegram_chat_id, preferred_lang
            FROM farmers
            WHERE district = ? AND primary_crop = ?
        ''', (district, crop))
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "farmer_id": r[0],
                "name": r[1],
                "phone": r[2],
                "district": r[3],
                "taluka": r[4],
                "chat_id": r[5],
                "lang": r[6]
            }
            for r in rows
        ]

    def compose_advisory(self, farmer_name: str, district: str, disease_key: str, custom_officer_note: Optional[str] = None) -> str:
        disease_info = DISEASE_KNOWLEDGE_BASE.get(
            disease_key.lower().replace(" ", "_"), 
            {"marathi_name": disease_key, "default_remedy": "कृषी सल्लागार केंद्राशी संपर्क साधावा."}
        )

        remedy_text = custom_officer_note if custom_officer_note else disease_info["default_remedy"]

        return (
            f"🚨 *[PeekRakshak कृषी चेतावणी अलर्ट]*\n\n"
            f"शेतकरी बांधव: *{farmer_name}*\n"
            f"📍 जिल्हा: *{district}*\n"
            f"⚠️ आढळलेला रोग: *{disease_info['marathi_name']}*\n\n"
            f"📋 *तातडीचा उपाय / फवारणी सल्ला:*\n{remedy_text}\n\n"
            f"🏛 _महा-अॅग्रो केंद्रात अनुदानित औषधे व खते उपलब्ध आहेत._\n"
            f"📞 टोल-फ्री कृषी मदत: १८००-१२०-१५५१"
        )

    def dispatch_alert(self, farmer: Dict, message_body: str, district: str, disease_key: str) -> Dict:
        """Dispatches multi-channel payload (Telegram live notification + GSM SMS log)."""
        target_chat = farmer.get("chat_id")
        delivery_status = "FAILED"
        channel_used = "telegram"

        # 1. Dispatch to device
        try:
            res = requests.post(self.telegram_url, json={
                "chat_id": target_chat,
                "text": message_body,
                "parse_mode": "Markdown"
            }, timeout=8)
            if res.json().get("ok"):
                delivery_status = "DELIVERED"
        except Exception as e:
            logger.error(f"Dispatch failed for {farmer['farmer_id']}: {str(e)}")

        # 2. Audit Trail Logging into DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alert_dispatches (district, disease, target_phone, message_body, delivery_channel, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (district, disease_key, farmer["phone"], message_body, channel_used, delivery_status))
        conn.commit()
        conn.close()

        return {
            "farmer_id": farmer["farmer_id"],
            "farmer_name": farmer["name"],
            "phone": farmer["phone"],
            "status": delivery_status
        }

    def execute_broadcast_pipeline(self, district: str, disease_key: str, custom_officer_note: Optional[str] = None) -> Dict:
        """Main execution entrypoint triggered by officer or auto-threshold."""
        disease_info = DISEASE_KNOWLEDGE_BASE.get(disease_key.lower().replace(" ", "_"), {"crop": "Cotton"})
        target_crop = disease_info["crop"]

        farmers = self.get_target_farmers(district, target_crop)
        if not farmers:
            return {"status": "skipped", "reason": f"No farmers found for {district} - {target_crop}"}

        dispatch_results = []
        for farmer in farmers:
            msg = self.compose_advisory(farmer["name"], district, disease_key, custom_officer_note)
            res = self.dispatch_alert(farmer, msg, district, disease_key)
            dispatch_results.append(res)

        return {
            "status": "completed",
            "district": district,
            "crop": target_crop,
            "disease": disease_key,
            "total_targeted": len(farmers),
            "dispatches": dispatch_results
        }

# Singleton instance
engine = OutbreakAlertEngine()

if __name__ == "__main__":
    print("Executing End-to-End Pipeline Test...\n")
    # Officer enters custom note for Yavatmal Cotton pink bollworm outbreak:
    result = engine.execute_broadcast_pipeline(
        district="Yavatmal",
        disease_key="pink_bollworm",
        custom_officer_note="कृषी विभागाच्या सूचनेनुसार आज संध्याकाळी सर्व कापूस उत्पादकांनी फेरोमोन ट्रॅप तपासावेत."
    )
    print("Pipeline Execution Summary:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
