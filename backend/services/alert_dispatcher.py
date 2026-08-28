import os
import requests
import json
import logging
import sqlite3
from typing import Dict, List

import requests
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

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_TEST_CHAT_ID = os.getenv(
    "TELEGRAM_TEST_CHAT_ID"
)


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(
    "AlertEngine"
)


# =========================================================
# ALERT ENGINE
# =========================================================

class OutbreakAlertEngine:

    def __init__(
        self,
        db_path: str = "data/peekrakshak.db",
    ):

        self.db_path = db_path

        self.bot_token = (
            TELEGRAM_BOT_TOKEN or ""
        )

        self.telegram_url = (
            "https://api.telegram.org/"
            f"bot{self.bot_token}/sendMessage"
        )

        self._init_db()

    # =====================================================
    # DATABASE
    # =====================================================

    def _init_db(self):

        os.makedirs(
            os.path.dirname(
                self.db_path
            ),
            exist_ok=True,
        )

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        # -------------------------------------------------
        # FARMERS
        # -------------------------------------------------

        cursor.execute(
            """
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
            """
        )

        # -------------------------------------------------
        # CASES
        # -------------------------------------------------

        cursor.execute(
            """
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
            """
        )

        # -------------------------------------------------
        # ALERT DISPATCHES
        # -------------------------------------------------

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

        # -------------------------------------------------
        # SAFE MIGRATION
        # -------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(alert_dispatches)"
        )

        columns = [
            column[1]
            for column in cursor.fetchall()
        ]

        if "crop" not in columns:
            cursor.execute(
                """
                ALTER TABLE alert_dispatches
                ADD COLUMN crop TEXT
                """
            )

        if "officer_message" not in columns:
            cursor.execute(
                """
                ALTER TABLE alert_dispatches
                ADD COLUMN officer_message TEXT
                """
            )

        # -------------------------------------------------
        # TEMPORARY TEST DATA
        #
        # Only YOUR Telegram account is used for testing.
        # Actual government/farmer database can replace this.
        # -------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM farmers"
        )

        farmer_count = cursor.fetchone()[0]

        if farmer_count == 0:

            if TELEGRAM_TEST_CHAT_ID:

                cursor.execute(
                    """
                    INSERT INTO farmers
                    (
                        farmer_id,
                        full_name,
                        phone_number,
                        district,
                        taluka,
                        primary_crop,
                        telegram_chat_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "TEST_USER_001",
                        "Kasim",
                        "TEST_ONLY",
                        "Yavatmal",
                        "Pusad",
                        "Cotton",
                        TELEGRAM_TEST_CHAT_ID,
                    ),
                )

        # -------------------------------------------------
        # SEED 6 OUTBREAK CASES
        # -------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM cases"
        )

        case_count = cursor.fetchone()[0]

        if case_count == 0:

            mock_cases = [
                (
                    f"CASE_YAV_{i}",
                    "Yavatmal",
                    "Cotton",
                    "pink_bollworm",
                    0.94,
                )
                for i in range(1, 7)
            ]

            cursor.executemany(
                """
                INSERT INTO cases
                (
                    case_id,
                    district,
                    crop,
                    disease_detected,
                    confidence
                )
                VALUES (?, ?, ?, ?, ?)
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

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                district,
                crop,
                disease_detected,
                COUNT(*) AS case_count
            FROM cases
            WHERE status = 'OPEN'
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
            }
            for row in rows
        ]

    # =====================================================
    # TEMPORARY TEST FARMER
    #
    # For now ONLY your Telegram account is targeted.
    # =====================================================

    def get_target_farmers(
        self,
        district: str,
        crop: str,
    ) -> List[Dict]:

        if not TELEGRAM_TEST_CHAT_ID:
            return []

        # Temporary test-only recipient.
        # Government database can replace this later.

        if (
            district.strip().lower()
            != "yavatmal"
        ):
            return []

        if (
            crop.strip().lower()
            != "cotton"
        ):
            return []

        return [
            {
                "farmer_id":
                    "TEST_USER_001",

                "name":
                    "Kasim",

                "phone":
                    "TEST_ONLY",

                "chat_id":
                    TELEGRAM_TEST_CHAT_ID,
            }
        ]

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
                "description":
                    "TELEGRAM_BOT_TOKEN is not configured.",
            }

        if not chat_id:
            return {
                "ok": False,
                "description":
                    "Telegram chat ID is missing.",
            }

        try:

            response = requests.post(
                self.telegram_url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                },
                timeout=10,
            )

            result = response.json()

            if response.ok and result.get(
                "ok"
            ):
                return result

            return {
                "ok": False,
                "description":
                    result.get(
                        "description",
                        "Telegram API rejected the message.",
                    ),
            }

        except requests.RequestException as error:

            logger.exception(
                "Telegram request failed"
            )

            return {
                "ok": False,
                "description":
                    str(error),
            }

        except ValueError:

            return {
                "ok": False,
                "description":
                    "Telegram returned invalid JSON.",
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

        farmers = self.get_target_farmers(
            district,
            crop,
        )

        if not farmers:

            return {
                "status": "skipped",
                "district": district,
                "crop": crop,
                "disease": disease,
                "total_farmers_notified": 0,
                "total_failed": 0,
                "dispatches": [],
                "message":
                    "No test Telegram recipient configured.",
            }

        dispatches = []

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        # -------------------------------------------------
        # SEND TO EACH TARGET
        # -------------------------------------------------

        for farmer in farmers:

            formatted_message = (
                f"🚨 कृषी विभाग चेतावणी अलर्ट - "
                f"{district}\n\n"

                f"शेतकरी बांधव: "
                f"{farmer['name']}\n"

                f"पीक: {crop} | "
                f"रोग: {disease}\n\n"

                f"📢 कृषी अधिकाऱ्यांचा संदेश:\n"
                f"{custom_message}\n\n"

                f"🏛 तातडीच्या मदतीसाठी "
                f"तालुका कृषी कार्यालयाशी संपर्क साधावा."
            )

            telegram_result = (
                self.send_telegram_message(
                    farmer["chat_id"],
                    formatted_message,
                )
            )

            if telegram_result.get("ok"):

                delivery_status = "DELIVERED"

                telegram_message_id = (
                    telegram_result
                    .get("result", {})
                    .get("message_id")
                )

            else:

                delivery_status = "FAILED"

                telegram_message_id = None

            # -------------------------------------------------
            # SAVE AUDIT LOG
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO alert_dispatches
                (
                    district,
                    crop,
                    disease,
                    target_phone,
                    officer_message,
                    delivery_channel,
                    status
                )
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
                "farmer_name":
                    farmer["name"],

                "phone":
                    farmer["phone"],

                "status":
                    delivery_status,
            }

            if telegram_message_id:
                dispatch[
                    "telegram_message_id"
                ] = telegram_message_id

            if not telegram_result.get("ok"):
                dispatch[
                    "error"
                ] = telegram_result.get(
                    "description",
                    "Telegram delivery failed.",
                )

            dispatches.append(
                dispatch
            )

        conn.commit()
        conn.close()

        # -------------------------------------------------
        # COUNTS
        # -------------------------------------------------

        delivered_count = sum(
            1
            for item in dispatches
            if item["status"] == "DELIVERED"
        )

        failed_count = sum(
            1
            for item in dispatches
            if item["status"] == "FAILED"
        )

        # -------------------------------------------------
        # FINAL STATUS
        # -------------------------------------------------

        if (
            delivered_count > 0
            and failed_count == 0
        ):
            final_status = "success"

        elif delivered_count > 0:
            final_status = "partial"

        else:
            final_status = "error"

        return {
            "status":
                final_status,

            "district":
                district,

            "crop":
                crop,

            "disease":
                disease,

            "total_farmers_notified":
                delivered_count,

            "total_failed":
                failed_count,

            "dispatches":
                dispatches,
        }


# =========================================================
# GLOBAL ENGINE
# =========================================================

engine = OutbreakAlertEngine()