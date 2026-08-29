import os
import sqlite3
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.ml.predictor import predict
from backend.rag.retriever import get_disease_information
from backend.schemas.case_schema import PredictionResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DISTRICT_COORDINATES = {
    "ahilyanagar (ahmednagar)": (19.0952, 74.7496),
    "ahmednagar": (19.0952, 74.7496),
    "akola": (20.7002, 77.0082),
    "amravati": (20.9374, 77.7796),
    "beed": (18.9891, 75.7601),
    "bhandara": (21.1667, 79.6500),
    "buldhana": (20.5312, 76.1834),
    "chandrapur": (19.9615, 79.2961),
    "chhatrapati sambhajinagar (aurangabad)": (19.8762, 75.3433),
    "aurangabad": (19.8762, 75.3433),
    "dharashiv (osmanabad)": (18.1856, 76.0416),
    "osmanabad": (18.1856, 76.0416),
    "dhule": (20.9042, 74.7749),
    "gadchiroli": (20.1849, 79.9948),
    "gondia": (21.4554, 80.1961),
    "hingoli": (19.7196, 77.1477),
    "jalgaon": (21.0077, 75.5626),
    "jalna": (19.8410, 75.8864),
    "kolhapur": (16.7050, 74.2433),
    "latur": (18.4088, 76.5604),
    "mumbai city": (18.9388, 72.8354),
    "mumbai suburban": (19.0760, 72.8777),
    "nagpur": (21.1458, 79.0882),
    "nanded": (19.1383, 77.3210),
    "nandurbar": (21.3700, 74.2400),
    "nashik": (19.9975, 73.7898),
    "palghar": (19.6967, 72.7655),
    "parbhani": (19.2686, 76.7708),
    "pune": (18.5204, 73.8567),
    "raigad": (18.5158, 73.1812),
    "ratnagiri": (16.9902, 73.3120),
    "sangli": (16.8524, 74.5815),
    "satara": (17.6805, 73.9936),
    "sindhudurg": (16.1216, 73.6934),
    "solapur": (17.6599, 75.9064),
    "thane": (19.2183, 72.9781),
    "wardha": (20.7453, 78.6022),
    "washim": (20.1110, 77.1340),
    "yavatmal": (20.3888, 78.1204),
}

DB_PATH = "data/peekrakshak.db"
CONFIDENCE_THRESHOLD = 0.75

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
}

@router.post(
    "/predict",
    response_model=PredictionResponse,
)
async def predict_disease(
    image: UploadFile = File(...),
    language: str = Form("en"),
    crop: str = Form("Cotton"),
    district: str = Form("Yavatmal"),
    farmer_name: str = Form("Ramesh Patil"),
    farmer_id: str = Form("MH_YAV_001"),
):
    if language not in ["en", "mr", "hi"]:
        raise HTTPException(status_code=400, detail="Language must be en, mr, or hi.")

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image type. Only JPG, JPEG and PNG images are allowed.",
        )

    try:
        image_bytes = await image.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read uploaded image.")

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    try:
        prediction = predict(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML prediction failed: {str(e)}")

    disease_key = prediction["disease"]
    confidence = float(prediction["confidence"])
    crop_detected = prediction.get("crop", crop)

    if confidence >= 0.85:
        severity = "High"
    elif confidence >= 0.60:
        severity = "Medium"
    else:
        severity = "Low"

    case_id = "CASE_" + uuid.uuid4().hex[:8].upper()

    # 1. Save uploaded image file to uploads directory
    file_ext = image.filename.split(".")[-1] if image.filename and "." in image.filename else "jpg"
    image_filename = f"{case_id}.{file_ext}"
    image_disk_path = os.path.join(UPLOAD_DIR, image_filename)
    try:
        with open(image_disk_path, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        print(f"[IMAGE SAVE WARNING] Could not write image to disk: {e}")

    # Relative path that FastAPI static mount serves
    image_url = f"http://127.0.0.1:8000/uploads/{image_filename}"

    # 2. Lookup district coordinates accurately
    normalized_district = district.strip().lower()
    lat, lon = DISTRICT_COORDINATES.get(normalized_district, (20.3888, 78.1204))

    # 3. Save into SQLite database
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO cases (
                case_id,
                farmer_id,
                farmer_name,
                district,
                crop,
                disease_detected,
                confidence,
                severity,
                latitude,
                longitude,
                image_url,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                farmer_id,
                farmer_name,
                district,
                crop_detected,
                disease_key,
                confidence,
                severity,
                lat,
                lon,
                image_url,
                "Pending Expert",
            ),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Failed to record case: {str(e)}")
    finally:
        conn.close()

    advisory_response = (
        "The AI confidence is below 75%. "
        "Your case has been logged for expert triage and manual prescription."
    )
    if confidence >= CONFIDENCE_THRESHOLD:
        disease_info = get_disease_information(disease_key)
        if disease_info:
            try:
                from backend.rag.llm import generate_response
                advisory_response = generate_response(
                    disease_info=disease_info,
                    confidence=confidence,
                    language=language,
                )
            except Exception as e:
                print(f"[LLM WARNING] Advisory generation skipped: {e}")

    return PredictionResponse(
        case_id=case_id,
        crop=crop_detected,
        disease=disease_key,
        confidence=confidence,
        status="Pending Expert",
        response=advisory_response,
        language=language,
    )