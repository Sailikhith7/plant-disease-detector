import os
import requests
import json
import logging
import sqlite3
from typing import Dict, List
from dotenv import load_dotenv

# =========================================================
# ENVIRONMENT
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Support both TELEGRAM_CHAT_ID and TELEGRAM_TEST_CHAT_ID keys
TELEGRAM_TEST_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_TEST_CHAT_ID")

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertEngine")


# =========================================================
# ALERT ENGINE
# =========================================================

class OutbreakAlertEngine:

    def __init__(
        self,
        db_path: str = "data/peekrakshak.db",
    ):
        self.db_path = db_path
        self.bot_token = TELEGRAM_BOT_TOKEN or ""
        self.telegram_url = (
            f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        )
        self._init_db()

    # =====================================================
    # DATABASE INITIALIZATION & MIGRATIONS
    # =====================================================

    def _init_db(self):
        os.makedirs(
            os.path.dirname(self.db_path),
            exist_ok=True,
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables without assuming columns exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id TEXT UNIQUE,
                full_name TEXT,
                phone TEXT,
                district TEXT,
                taluka TEXT,
                primary_crop TEXT,
                telegram_chat_id TEXT
            )
            """
        )

        # Automatically add any missing columns to 'farmers' if table already existed
        cursor.execute("PRAGMA table_info(farmers)")
        farmer_cols = [c[1] for c in cursor.fetchall()]
        
        required_farmer_columns = {
            "phone": "TEXT",
            "taluka": "TEXT",
            "primary_crop": "TEXT",
            "telegram_chat_id": "TEXT"
        }
        for col_name, col_type in required_farmer_columns.items():
            if col_name not in farmer_cols:
                cursor.execute(f"ALTER TABLE farmers ADD COLUMN {col_name} {col_type}")

        # Cases Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE,
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
            """
        )

        # Alert Dispatches Table
        cursor.execute(
            """
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
            """
        )

        # Safe Schema Migrations for Dispatches & Cases
        cursor.execute("PRAGMA table_info(alert_dispatches)")
        dispatch_cols = [c[1] for c in cursor.fetchall()]
        if "crop" not in dispatch_cols:
            cursor.execute("ALTER TABLE alert_dispatches ADD COLUMN crop TEXT")
        if "officer_message" not in dispatch_cols:
            cursor.execute("ALTER TABLE alert_dispatches ADD COLUMN officer_message TEXT")

        cursor.execute("PRAGMA table_info(cases)")
        case_cols = [c[1] for c in cursor.fetchall()]
        if "farmer_id" not in case_cols:
            cursor.execute("ALTER TABLE cases ADD COLUMN farmer_id TEXT")
        if "farmer_name" not in case_cols:
            cursor.execute("ALTER TABLE cases ADD COLUMN farmer_name TEXT")

        # Seed Test Farmer
        cursor.execute("SELECT COUNT(*) FROM farmers")
        if cursor.fetchone()[0] == 0 and TELEGRAM_TEST_CHAT_ID:
            cursor.execute(
                """
                INSERT OR IGNORE INTO farmers
                (farmer_id, full_name, phone, district, taluka, primary_crop, telegram_chat_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "TEST_USER_001",
                    "Kasim",
                    "+91-9876543210",
                    "Yavatmal",
                    "Pusad",
                    "Cotton",
                    TELEGRAM_TEST_CHAT_ID,
                ),
            )

        # Seed 6 Mock Outbreak Cases
        cursor.execute("SELECT COUNT(*) FROM cases")
        if cursor.fetchone()[0] == 0:
            mock_cases = [
                (
                    f"CASE_YAV_{i}",
                    "TEST_USER_001",
                    "Kasim",
                    "Yavatmal",
                    "Cotton",
                    "Pink Bollworm",
                    0.94,
                    "High",
                    20.3888,
                    78.1204,
                    "Pending Expert"
                )
                for i in range(1, 7)
            ]
            cursor.executemany(
                """
                INSERT OR IGNORE INTO cases
                (case_id, farmer_id, farmer_name, district, crop, disease_detected, confidence, severity, latitude, longitude, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                mock_cases,
            )

        conn.commit()
        conn.close()

    # =====================================================
    # OUTBREAK SUMMARY
    # =====================================================

    def get_outbreak_summary(
        self,
        threshold: int = 5,
    ) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Matches both 'OPEN' and 'Pending Expert' cases
        cursor.execute(
            """
            SELECT
                district,
                crop,
                disease_detected,
                COUNT(*) AS case_count
            FROM cases
            WHERE LOWER(status) NOT LIKE '%resolve%'
            GROUP BY
                district,
                crop,
                disease_detected
            HAVING case_count >= ?
            """,
            (threshold,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "district": row[0],
                "crop": row[1],
                "disease": row[2],
                "case_count": row[3],
                "threshold_breached": True,
                "risk": "High",
                "severity": "High"
            }
            for row in rows
        ]

    # =====================================================
    # TARGET FARMERS RETRIEVAL
    # =====================================================

    def get_target_farmers(
        self,
        district: str,
        crop: str,
    ) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Look up matching farmers by district
        cursor.execute(
            """
            SELECT farmer_id, full_name, phone, telegram_chat_id
            FROM farmers
            WHERE LOWER(district) = LOWER(?)
            """,
            (district.strip(),)
        )
        rows = cursor.fetchall()
        conn.close()

        farmers = []
        for r in rows:
            chat_id = r[3] or TELEGRAM_TEST_CHAT_ID
            if chat_id:
                farmers.append({
                    "farmer_id": r[0],
                    "name": r[1] or "Farmer",
                    "phone": r[2] or "N/A",
                    "chat_id": str(chat_id)
                })

        # Fallback to test chat id if no district match found
        if not farmers and TELEGRAM_TEST_CHAT_ID:
            farmers.append({
                "farmer_id": "FALLBACK_TEST",
                "name": "District Officer / Farmer",
                "phone": "+91-9876543210",
                "chat_id": str(TELEGRAM_TEST_CHAT_ID)
            })

        return farmers

    # =====================================================
    # SEND TELEGRAM MESSAGE
    # =====================================================

    def send_telegram_message(
        self,
        chat_id: str,
        text: str,
    ) -> Dict:
        if not self.bot_token:
            return {
                "ok": False,
                "description": "TELEGRAM_BOT_TOKEN is not configured.",
            }

        if not chat_id:
            return {
                "ok": False,
                "description": "Telegram chat ID is missing.",
            }

        try:
            response = requests.post(
                self.telegram_url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                },
                timeout=10,
            )
            result = response.json()
            if response.ok and result.get("ok"):
                return result

            # Retry without markdown if parsing fails
            retry_res = requests.post(
                self.telegram_url,
                json={
                    "chat_id": chat_id,
                    "text": text
                },
                timeout=10,
            )
            return retry_res.json()

        except requests.RequestException as error:
            logger.exception("Telegram request failed")
            return {
                "ok": False,
                "description": str(error),
            }
        except ValueError:
            return {
                "ok": False,
                "description": "Telegram returned invalid JSON.",
            }

    # =====================================================
    # BROADCAST CUSTOM OFFICER MESSAGE
    # =====================================================

    def dispatch_custom_officer_broadcast(
        self,
        district: str,
        crop: str,
        disease: str,
        custom_message: str,
    ) -> Dict:
        farmers = self.get_target_farmers(district, crop)

        if not farmers:
            return {
                "status": "skipped",
                "district": district,
                "crop": crop,
                "disease": disease,
                "total_farmers_notified": 0,
                "total_failed": 0,
                "dispatches": [],
                "message": "No Telegram recipients found.",
            }

        dispatches = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for farmer in farmers:
            formatted_message = (
                f"🚨 *कृषी विभाग चेतावणी अलर्ट - {district}*\n\n"
                f"👤 *शेतकरी बांधव:* {farmer['name']}\n"
                f"🌱 *पीक:* {crop} | *रोग:* {disease}\n\n"
                f"📢 *कृषी अधिकाऱ्यांचा संदेश:*\n{custom_message}\n\n"
                f"🏛 *तातडीच्या मदतीसाठी तालुका कृषी कार्यालयाशी संपर्क साधावा.*"
            )

            telegram_result = self.send_telegram_message(
                farmer["chat_id"],
                formatted_message,
            )

            if telegram_result.get("ok"):
                delivery_status = "DELIVERED"
                telegram_message_id = (
                    telegram_result.get("result", {}).get("message_id")
                )
            else:
                delivery_status = "FAILED"
                telegram_message_id = None

            cursor.execute(
                """
                INSERT INTO alert_dispatches
                (district, crop, disease, target_phone, officer_message, delivery_channel, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    district,
                    crop,
                    disease,
                    farmer["phone"],
                    custom_message,
                    "telegram",
                    delivery_status,
                ),
            )

            dispatch = {
                "farmer_name": farmer["name"],
                "phone": farmer["phone"],
                "status": delivery_status,
            }

            if telegram_message_id:
                dispatch["telegram_message_id"] = telegram_message_id

            if not telegram_result.get("ok"):
                dispatch["error"] = telegram_result.get(
                    "description", "Telegram delivery failed."
                )

            dispatches.append(dispatch)

        conn.commit()
        conn.close()

        delivered_count = sum(1 for item in dispatches if item["status"] == "DELIVERED")
        failed_count = sum(1 for item in dispatches if item["status"] == "FAILED")

        if delivered_count > 0 and failed_count == 0:
            final_status = "success"
        elif delivered_count > 0:
            final_status = "partial"
        else:
            final_status = "error"

        return {
            "status": final_status,
            "district": district,
            "crop": crop,
            "disease": disease,
            "total_farmers_notified": delivered_count,
            "total_failed": failed_count,
            "dispatches": dispatches,
        }


# =========================================================
# GLOBAL ENGINE INSTANCE
# =========================================================

engine = OutbreakAlertEngine()