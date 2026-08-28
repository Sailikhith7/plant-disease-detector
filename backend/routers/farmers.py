import sqlite3

from fastapi import APIRouter, HTTPException

from backend.schemas.farmer_schema import FarmerCreate, FarmerResponse


router = APIRouter(
    prefix="/api/farmers",
    tags=["Farmers"]
)

DB_PATH = "data/peekrakshak.db"


@router.post("/", response_model=FarmerResponse)
def register_farmer(farmer: FarmerCreate):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO farmers (
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
                farmer.farmer_id,
                farmer.full_name,
                farmer.phone_number,
                farmer.district,
                farmer.taluka,
                farmer.primary_crop,
                farmer.telegram_chat_id
            )
        )

        farmer_db_id = cursor.lastrowid

        conn.commit()

        return FarmerResponse(
            id=farmer_db_id,
            **farmer.model_dump()
        )

    except sqlite3.IntegrityError:
        conn.rollback()

        raise HTTPException(
            status_code=400,
            detail="Farmer ID already exists."
        )

    finally:
        conn.close()


@router.get("/")
def list_farmers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            farmer_id,
            full_name,
            phone_number,
            district,
            taluka,
            primary_crop,
            telegram_chat_id
        FROM farmers
        ORDER BY id
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "farmer_id": row[1],
            "full_name": row[2],
            "phone_number": row[3],
            "district": row[4],
            "taluka": row[5],
            "primary_crop": row[6],
            "telegram_chat_id": row[7]
        }
        for row in rows
    ]