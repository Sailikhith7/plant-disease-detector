import os
import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

DB_PATH = "data/peekrakshak.db"

os.makedirs(
    os.path.dirname(DB_PATH),
    exist_ok=True
)


# =========================================================
# REALISTIC DEMO CASE DATA
#
# Confidence >= 75 -> Resolved
# Confidence < 75  -> Pending Expert
#
# This keeps the existing /api/cases/ contract unchanged.
# =========================================================

DEMO_CASES = [

    # -----------------------------------------------------
    # YAVATMAL - PINK BOLLWORM OUTBREAK
    # 6 cases
    # -----------------------------------------------------

    {
        "case_id": "CASE_YAV_001",
        "farmer_id": "MH_YAV_001",
        "farmer_name": "Ramesh Patil",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "confidence": 94,
        "district": "Yavatmal",
        "severity": "High",
        "latitude": 20.389,
        "longitude": 78.130,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_YAV_002",
        "farmer_id": "MH_YAV_002",
        "farmer_name": "Sunita Jadhav",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "confidence": 91,
        "district": "Yavatmal",
        "severity": "High",
        "latitude": 20.420,
        "longitude": 78.020,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_YAV_003",
        "farmer_id": "MH_YAV_004",
        "farmer_name": "Mahesh Pawar",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "confidence": 89,
        "district": "Yavatmal",
        "severity": "High",
        "latitude": 20.150,
        "longitude": 78.350,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_YAV_004",
        "farmer_id": "MH_YAV_005",
        "farmer_name": "Vijay Rathod",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "confidence": 87,
        "district": "Yavatmal",
        "severity": "High",
        "latitude": 20.310,
        "longitude": 78.080,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_YAV_005",
        "farmer_id": "MH_YAV_001",
        "farmer_name": "Ramesh Patil",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "confidence": 72,
        "district": "Yavatmal",
        "severity": "High",
        "latitude": 20.389,
        "longitude": 78.130,
        "status": "Pending Expert",
    },

    {
        "case_id": "CASE_YAV_006",
        "farmer_id": "MH_YAV_002",
        "farmer_name": "Sunita Jadhav",
        "crop": "Cotton",
        "disease": "pink_bollworm",
        "confidence": 61,
        "district": "Yavatmal",
        "severity": "High",
        "latitude": 20.420,
        "longitude": 78.020,
        "status": "Pending Expert",
    },


    # -----------------------------------------------------
    # NAGPUR
    # -----------------------------------------------------

    {
        "case_id": "CASE_NAG_001",
        "farmer_id": "MH_NAG_001",
        "farmer_name": "Sanjay Deshmukh",
        "crop": "Soybean",
        "disease": "soybean_rust",
        "confidence": 88,
        "district": "Nagpur",
        "severity": "Medium",
        "latitude": 21.146,
        "longitude": 79.088,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_NAG_002",
        "farmer_id": "MH_NAG_002",
        "farmer_name": "Kavita Wankhede",
        "crop": "Cotton",
        "disease": "bollworm",
        "confidence": 76,
        "district": "Nagpur",
        "severity": "Medium",
        "latitude": 21.110,
        "longitude": 79.120,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_NAG_003",
        "farmer_id": "MH_NAG_003",
        "farmer_name": "Ramesh Gawande",
        "crop": "Orange",
        "disease": "citrus_canker",
        "confidence": 93,
        "district": "Nagpur",
        "severity": "High",
        "latitude": 21.250,
        "longitude": 78.980,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_NAG_004",
        "farmer_id": "MH_NAG_004",
        "farmer_name": "Mohan Borkar",
        "crop": "Soybean",
        "disease": "soybean_rust",
        "confidence": 68,
        "district": "Nagpur",
        "severity": "Low",
        "latitude": 21.050,
        "longitude": 79.020,
        "status": "Pending Expert",
    },


    # -----------------------------------------------------
    # NASHIK
    # -----------------------------------------------------

    {
        "case_id": "CASE_NAS_001",
        "farmer_id": "MH_NAS_001",
        "farmer_name": "Rahul Shinde",
        "crop": "Tomato",
        "disease": "early_blight",
        "confidence": 84,
        "district": "Nashik",
        "severity": "Medium",
        "latitude": 20.005,
        "longitude": 73.780,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_NAS_002",
        "farmer_id": "MH_NAS_002",
        "farmer_name": "Kiran Pawar",
        "crop": "Grapes",
        "disease": "downy_mildew",
        "confidence": 90,
        "district": "Nashik",
        "severity": "High",
        "latitude": 20.180,
        "longitude": 73.990,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_NAS_003",
        "farmer_id": "MH_NAS_003",
        "farmer_name": "Sachin More",
        "crop": "Onion",
        "disease": "purple_blotch",
        "confidence": 71,
        "district": "Nashik",
        "severity": "Medium",
        "latitude": 20.090,
        "longitude": 73.780,
        "status": "Pending Expert",
    },

    {
        "case_id": "CASE_NAS_004",
        "farmer_id": "MH_NAS_004",
        "farmer_name": "Vishal Patil",
        "crop": "Tomato",
        "disease": "early_blight",
        "confidence": 64,
        "district": "Nashik",
        "severity": "Low",
        "latitude": 20.120,
        "longitude": 73.840,
        "status": "Pending Expert",
    },


    # -----------------------------------------------------
    # NANDED
    # -----------------------------------------------------

    {
        "case_id": "CASE_NAN_001",
        "farmer_id": "MH_NAN_001",
        "farmer_name": "Suresh Shinde",
        "crop": "Soybean",
        "disease": "soybean_rust",
        "confidence": 82,
        "district": "Nanded",
        "severity": "Medium",
        "latitude": 19.150,
        "longitude": 77.320,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_NAN_002",
        "farmer_id": "MH_NAN_002",
        "farmer_name": "Datta Jadhav",
        "crop": "Cotton",
        "disease": "leaf_curl",
        "confidence": 74,
        "district": "Nanded",
        "severity": "Medium",
        "latitude": 19.250,
        "longitude": 77.500,
        "status": "Pending Expert",
    },

    {
        "case_id": "CASE_NAN_003",
        "farmer_id": "MH_NAN_004",
        "farmer_name": "Vivek Deshmukh",
        "crop": "Cotton",
        "disease": "leaf_curl",
        "confidence": 88,
        "district": "Nanded",
        "severity": "High",
        "latitude": 19.080,
        "longitude": 77.300,
        "status": "Resolved",
    },


    # -----------------------------------------------------
    # KOLHAPUR
    # -----------------------------------------------------

    {
        "case_id": "CASE_KOL_001",
        "farmer_id": "MH_KOL_001",
        "farmer_name": "Prakash Patil",
        "crop": "Sugarcane",
        "disease": "red_rot",
        "confidence": 92,
        "district": "Kolhapur",
        "severity": "High",
        "latitude": 16.705,
        "longitude": 74.240,
        "status": "Resolved",
    },

    {
        "case_id": "CASE_KOL_002",
        "farmer_id": "MH_KOL_002",
        "farmer_name": "Sunil More",
        "crop": "Sugarcane",
        "disease": "red_rot",
        "confidence": 69,
        "district": "Kolhapur",
        "severity": "Low",
        "latitude": 16.750,
        "longitude": 74.300,
        "status": "Pending Expert",
    },

    {
        "case_id": "CASE_KOL_003",
        "farmer_id": "MH_KOL_003",
        "farmer_name": "Meena Pawar",
        "crop": "Sugarcane",
        "disease": "smut",
        "confidence": 79,
        "district": "Kolhapur",
        "severity": "Medium",
        "latitude": 16.680,
        "longitude": 74.260,
        "status": "Resolved",
    },
]


# =========================================================
# DATABASE SETUP
#
# Kept for existing resolve/history functionality.
# =========================================================

def init_cases_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
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
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expert_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            expert_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


init_cases_db()


# =========================================================
# GET ALL CASES
# =========================================================

@router.get("")
@router.get("/")
def list_cases():

    cases = []

    for item in DEMO_CASES:

        cases.append({
            "case_id": item["case_id"],
            "farmer_id": item["farmer_id"],
            "farmer_name": item["farmer_name"],
            "crop": item["crop"],
            "disease": item["disease"],
            "confidence": item["confidence"],
            "district": item["district"],
            "severity": item["severity"],
            "latitude": item["latitude"],
            "longitude": item["longitude"],
            "image_url": None,
            "status": item["status"],
            "created_at": "2026-08-30 10:00:00",
        })

    return {
        "status": "success",
        "cases": cases,
    }


# =========================================================
# GET SINGLE CASE
# =========================================================

@router.get("/{case_id}")
def get_case(case_id: str):

    for item in DEMO_CASES:

        if item["case_id"] == case_id:

            return {
                "case_id": item["case_id"],
                "farmer_id": item["farmer_id"],
                "farmer_name": item["farmer_name"],
                "district": item["district"],
                "crop": item["crop"],
                "disease": item["disease"],
                "confidence": item["confidence"],
                "severity": item["severity"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                "image_url": None,
                "status": item["status"],
                "expert_response": None,
                "created_at": "2026-08-30 10:00:00",
            }

    raise HTTPException(
        status_code=404,
        detail="Case not found."
    )


# =========================================================
# EXPERT RESPONSE
# =========================================================

class ExpertResponse(BaseModel):
    expert_response: str


@router.post("/{case_id}/resolve")
def resolve_case(
    case_id: str,
    data: ExpertResponse
):

    found = any(
        item["case_id"] == case_id
        for item in DEMO_CASES
    )

    if not found:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    # Keep audit trail in the existing database.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO expert_responses
        (
            case_id,
            expert_response
        )
        VALUES (?, ?)
        """,
        (
            case_id,
            data.expert_response,
        )
    )

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "case_id": case_id,
        "message": "Case resolved successfully.",
        "expert_response": data.expert_response,
    } 