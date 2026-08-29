from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import sqlite3
import uuid

from backend.ml.predictor import predict
from backend.rag.retriever import get_disease_information
from backend.schemas.case_schema import PredictionResponse


router = APIRouter()

DB_PATH = "data/peekrakshak.db"

# =========================================================
# CONFIDENCE THRESHOLD
# =========================================================

CONFIDENCE_THRESHOLD = 0.75


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
}


# =========================================================
# SIMPLE INPUTS CHECK
# =========================================================

@router.get("/inputs")
def list_inputs():
    return {
        "status": "success",
        "inputs": [],
    }


# =========================================================
# PLANT DISEASE PREDICTION
# =========================================================

@router.post(
    "/predict",
    response_model=PredictionResponse,
)
async def predict_disease(
    image: UploadFile = File(...),
    language: str = Form("en"),
    district: str = Form("Yavatmal"),
    farmer_name: str = Form("App Farmer"),
    farmer_id: str = Form("MH_YAV_001"),
):

    # -----------------------------------------------------
    # 1. Validate language
    # -----------------------------------------------------

    if language not in ["en", "mr", "hi"]:
        raise HTTPException(
            status_code=400,
            detail="Language must be en, mr, or hi.",
        )

    # -----------------------------------------------------
    # 2. Validate image
    # -----------------------------------------------------

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image type. "
                "Only JPG, JPEG and PNG images are allowed."
            ),
        )

    # -----------------------------------------------------
    # 3. Read image
    # -----------------------------------------------------

    try:
        image_bytes = await image.read()

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read uploaded image.",
        )

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    # -----------------------------------------------------
    # 4. ML prediction
    # -----------------------------------------------------

    try:
        prediction = predict(image_bytes)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ML prediction failed: {str(e)}",
        )

    disease_key = prediction["disease"]
    confidence = float(prediction["confidence"])
    crop = prediction["crop"]

    print(
        f"[ML] Disease={disease_key}, "
        f"Confidence={confidence:.2%}"
    )

    # =====================================================
    # 5. HIGH CONFIDENCE
    #
    # >= 75%
    #
    # ML → RAG → LLM → Mobile App
    # =====================================================

    if confidence >= CONFIDENCE_THRESHOLD:

        print("[ROUTING] HIGH CONFIDENCE → DIRECT MOBILE")

        disease_info = get_disease_information(
            disease_key
        )

        if disease_info is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No knowledge-base information found "
                    f"for disease: {disease_key}"
                ),
            )

        try:

            from backend.rag.llm import generate_response

            response = generate_response(
                disease_info=disease_info,
                confidence=confidence,
                language=language,
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM generation failed: {str(e)}",
            )

        return PredictionResponse(
            case_id=None,
            crop=crop,
            disease=disease_key,
            confidence=confidence,
            status="Direct Diagnosis",
            response=response,
            language=language,
        )

    # =====================================================
    # 6. LOW CONFIDENCE
    #
    # < 75%
    #
    # ML → DATABASE → DASHBOARD → EXPERT
    # =====================================================

    print("[ROUTING] LOW CONFIDENCE → EXPERT DASHBOARD")

    case_id = "CASE_" + uuid.uuid4().hex[:8].upper()

    conn = sqlite3.connect(DB_PATH)

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO cases (
                case_id,
                farmer_id,
                district,
                crop,
                disease_detected,
                confidence,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                farmer_id,
                district,
                crop,
                disease_key,
                confidence,
                "PENDING_EXPERT",
            ),
        )

        conn.commit()

    except Exception as e:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create expert case: {str(e)}",
        )

    finally:
        conn.close()

    return PredictionResponse(
        case_id=case_id,
        crop=crop,
        disease=disease_key,
        confidence=confidence,
        status="Pending Expert",
        response=(
            "The AI confidence is below 75%. "
            "Your case has been sent to an agricultural "
            "expert for verification."
        ),
        language=language,
    )