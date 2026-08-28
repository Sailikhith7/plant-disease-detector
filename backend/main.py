import os
from typing import List, Dict

import httpx

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================================================
# LOAD ENV
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_TEST_CHAT_ID = os.getenv(
    "TELEGRAM_TEST_CHAT_ID"
)

demo_farmers = [
    {
        "farmer_name": "Kasim",
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "telegram_chat_id": TELEGRAM_TEST_CHAT_ID or "",
    }
]
# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="PikRakshak Backend",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class BroadcastRequest(BaseModel):
    district: str
    crop: str
    disease: str
    custom_message: str


# =========================================================
# DEMO COMPLAINT DATA
#
# IMPORTANT:
# These represent 6 reported complaints.
# This keeps the outbreak threshold test working.
# =========================================================

demo_complaints: List[Dict[str, str]] = [
    {
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
    },
    {
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
    },
    {
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
    },
    {
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
    },
    {
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
    },
    {
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
    },
]


# =========================================================
# TELEGRAM TEST RECIPIENT
#
# This is your real Telegram chat ID.
# Later this will come from the real farmer database.
# =========================================================

demo_farmers: List[Dict[str, str]] = [
    {
        "farmer_name": "Telegram Test Farmer",
        "district": "Yavatmal",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "telegram_chat_id":
            TELEGRAM_TEST_CHAT_ID or "",
    }
]


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_value(value: str) -> str:
    return (
        value
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


# =========================================================
# ROOT / HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "service": "PikRakshak Backend",
        "status": "running",
        "telegram_configured":
            bool(TELEGRAM_BOT_TOKEN),
    }


# =========================================================
# TELEGRAM SEND HELPER
# =========================================================

async def send_telegram_message(
    chat_id: str,
    text: str,
):
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    if not chat_id:
        raise RuntimeError(
            "Telegram chat ID is missing."
        )

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    async with httpx.AsyncClient(
        timeout=15
    ) as client:

        response = await client.post(
            url,
            json=payload,
        )

    result = response.json()

    if not response.is_success:
        raise RuntimeError(
            result.get(
                "description",
                "Telegram API request failed.",
            )
        )

    if not result.get("ok"):
        raise RuntimeError(
            result.get(
                "description",
                "Telegram message failed.",
            )
        )

    return result


# =========================================================
# TELEGRAM CONNECTION TEST
# =========================================================

@app.get("/api/telegram/test")
async def telegram_test():

    try:

        result = await send_telegram_message(
            TELEGRAM_TEST_CHAT_ID,
            (
                "PikRakshak Telegram test alert ✅\n\n"
                "Actual Telegram connection is working."
            ),
        )

        return {
            "status": "success",
            "message":
                "Telegram message sent successfully.",
            "telegram_message_id":
                result["result"]["message_id"],
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error),
        }


# =========================================================
# OUTBREAK DETECTION
#
# GET:
# /api/alerts/outbreaks?threshold=5
# =========================================================

@app.get("/api/alerts/outbreaks")
def get_outbreaks(
    threshold: int = 5,
):

    if threshold < 1:
        threshold = 1

    grouped: Dict[
        tuple[str, str, str],
        List[Dict[str, str]]
    ] = {}

    for complaint in demo_complaints:

        key = (
            normalize_value(
                complaint["district"]
            ),
            normalize_value(
                complaint["crop"]
            ),
            normalize_value(
                complaint["disease"]
            ),
        )

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(
            complaint
        )

    outbreaks = []

    for (
        district,
        crop,
        disease,
    ), matching_complaints in grouped.items():

        case_count = len(
            matching_complaints
        )

        if case_count >= threshold:

            outbreaks.append(
                {
                    "district":
                        matching_complaints[0][
                            "district"
                        ],

                    "crop":
                        matching_complaints[0][
                            "crop"
                        ],

                    "disease":
                        matching_complaints[0][
                            "disease"
                        ],

                    "case_count":
                        case_count,
                }
            )

    return outbreaks


# =========================================================
# BROADCAST ADVISORY
#
# POST:
# /api/alerts/broadcast
#
# NOW ACTUALLY SENDS THROUGH TELEGRAM
# =========================================================

@app.post("/api/alerts/broadcast")
async def broadcast_advisory(
    request: BroadcastRequest,
):

    district = normalize_value(
        request.district
    )

    crop = normalize_value(
        request.crop
    )

    disease = normalize_value(
        request.disease
    )

    message = request.custom_message.strip()

    if not message:

        return {
            "status": "error",
            "detail":
                "Custom advisory message is required.",
        }

    # -----------------------------------------------------
    # FILTER FARMERS
    #
    # Later this will come from PostgreSQL/database.
    # -----------------------------------------------------

    matched_farmers = [
        farmer
        for farmer in demo_farmers

        if normalize_value(
            farmer["district"]
        ) == district

        and normalize_value(
            farmer["crop"]
        ) == crop

        and normalize_value(
            farmer["disease"]
        ) == disease

        and farmer["telegram_chat_id"]
    ]

    # -----------------------------------------------------
    # SEND REAL TELEGRAM MESSAGE
    # -----------------------------------------------------

    dispatches = []

    for farmer in matched_farmers:

        try:

            result = (
                await send_telegram_message(
                    farmer[
                        "telegram_chat_id"
                    ],
                    message,
                )
            )

            dispatches.append(
                {
                    "farmer_name":
                        farmer["farmer_name"],

                    "telegram_chat_id":
                        farmer[
                            "telegram_chat_id"
                        ],

                    "status":
                        "DELIVERED",

                    "telegram_message_id":
                        result[
                            "result"
                        ][
                            "message_id"
                        ],
                }
            )

        except Exception as error:

            dispatches.append(
                {
                    "farmer_name":
                        farmer["farmer_name"],

                    "telegram_chat_id":
                        farmer[
                            "telegram_chat_id"
                        ],

                    "status":
                        "FAILED",

                    "error":
                        str(error),
                }
            )

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

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    if delivered_count > 0 and failed_count == 0:

        status = "success"

    elif delivered_count > 0:

        status = "partial"

    else:

        status = "error"

    return {
        "status":
            status,

        "district":
            request.district,

        "crop":
            request.crop,

        "disease":
            request.disease,

        "total_farmers_notified":
            delivered_count,

        "total_failed":
            failed_count,

        "dispatches":
            dispatches,
    }