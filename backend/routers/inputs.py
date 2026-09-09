import os
import uuid
import asyncio
import traceback

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
)

from sqlalchemy.orm import Session

from backend.database import get_db, Case

# ============================================================
# ML MODELS
# ============================================================

from backend.ml.disease_predictor import predict as predict_disease_model
from backend.ml.pest_predictor import predict as predict_pest_model

# ============================================================
# RAG / LLM
# ============================================================

from backend.rag.retriever import (
    get_disease_information,
    get_pest_information,
)
from backend.rag.llm import generate_response

# ============================================================
# SCHEMA
# ============================================================

from backend.schemas.case_schema import PredictionResponse

# ============================================================
# CLOUD STORAGE
# ============================================================

from backend.services.cloud_storage import upload_image_to_cloud

# ============================================================
# VOICE SERVICE
# ============================================================

try:
    from backend.services.voice_service import generate_regional_audio

    voice_service_loaded = True

except ImportError:
    voice_service_loaded = False


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ============================================================
# DISTRICT COORDINATES
# ============================================================

DISTRICT_COORDINATES = {

    "ahilyanagar (ahmednagar)": (19.0952, 74.7496),

    "ahmednagar": (19.0952, 74.7496),

    "akola": (20.7002, 77.0082),

    "amravati": (20.9374, 77.7796),

    "beed": (18.9891, 75.7601),

    "bhandara": (21.1667, 79.6500),

    "buldhana": (20.5312, 76.1834),

    "chandrapur": (19.9615, 79.2961),

    "chhatrapati sambhajinagar (aurangabad)": (
        19.8762,
        75.3433
    ),

    "aurangabad": (19.8762, 75.3433),

    "dharashiv (osmanabad)": (
        18.1856,
        76.0416
    ),

    "osmanabad": (
        18.1856,
        76.0416
    ),

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


# ============================================================
# CONFIGURATION
# ============================================================

CONFIDENCE_THRESHOLD = 0.75

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
}


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

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

    db: Session = Depends(get_db),

):

    # ========================================================
    # 1. VALIDATE LANGUAGE
    # ========================================================

    if language not in ["en", "mr", "hi"]:

        raise HTTPException(
            status_code=400,
            detail="Language must be en, mr, or hi."
        )


    # ========================================================
    # 2. VALIDATE IMAGE TYPE
    # ========================================================

    if image.content_type not in ALLOWED_IMAGE_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image type. "
                "Only JPG, JPEG and PNG images are allowed."
            ),
        )


    # ========================================================
    # 3. READ IMAGE
    # ========================================================

    try:

        image_bytes = await image.read()

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Could not read uploaded image."
        )


    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )


    # ========================================================
    # 4. DISEASE + PEST ML PREDICTION
    # ========================================================

    # --------------------------------------------------------
    # Disease prediction
    # --------------------------------------------------------

    try:

        disease_prediction = predict(
            image_bytes
        )

    except Exception as e:

        print(
            f"[DISEASE ML ERROR] {e}"
        )

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Disease ML prediction failed: {str(e)}"
            ),
        )


    # --------------------------------------------------------
    # Pest prediction
    # --------------------------------------------------------

    try:

        pest_prediction = predict_pest(
            image_bytes
        )

    except Exception as e:

        print(
            f"[PEST ML ERROR] {e}"
        )

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Pest ML prediction failed: {str(e)}"
            ),
        )


    # ========================================================
    # 5. EXTRACT DISEASE RESULT
    # ========================================================

    disease_key = disease_prediction.get(
        "disease",
        "Unknown"
    )

    confidence = float(
        disease_prediction.get(
            "confidence",
            0.0
        )
    )

    crop_detected = disease_prediction.get(
        "crop",
        crop
    )


    # ========================================================
    # 6. EXTRACT PEST RESULT
    # ========================================================

    pest_key = pest_prediction.get(
        "pest",
        "Unknown"
    )

    pest_confidence = float(
        pest_prediction.get(
            "confidence",
            0.0
        )
    )

    pest_status = pest_prediction.get(
        "status",
        "uncertain"
    )

    pest_top_3 = pest_prediction.get(
        "top_3",
        []
    )


    # ========================================================
    # 7. DETERMINE DISEASE SEVERITY
    # ========================================================

    if confidence >= 0.85:

        severity = "High"

    elif confidence >= 0.60:

        severity = "Medium"

    else:

        severity = "Low"


    # ========================================================
    # 8. GENERATE CASE ID
    # ========================================================

    case_id = (
        "CASE_"
        + uuid.uuid4().hex[:8].upper()
    )


    # ========================================================
    # 9. GET DISEASE INFORMATION FROM RAG
    # ========================================================

    disease_info = get_disease_information(
        disease_key
    )


    # --------------------------------------------------------
    # Fallback disease information
    # --------------------------------------------------------

    if not disease_info:

        disease_info = {

            "name": disease_key,

            "management": [
                "Consult local agricultural officer."
            ],

            "prevention": [
                "Maintain field sanitation."
            ],

        }


    # ========================================================
    # 10. IMAGE UPLOAD
    # ========================================================

    async def _upload_image():

        # Cloudinary SDK is blocking.
        # Run it in a separate thread so the
        # FastAPI event loop is not blocked.

        return await asyncio.to_thread(
            upload_image_to_cloud,
            image_bytes
        )


    # ========================================================
    # 11. BUILD DISEASE ADVISORY
    # ========================================================

    async def _build_advisory():

        advisory_text = ""


        # ----------------------------------------------------
        # Generate LLM advisory only when disease confidence
        # is sufficiently high.
        # ----------------------------------------------------

        if confidence >= CONFIDENCE_THRESHOLD:

            try:

                advisory_text = await asyncio.to_thread(

                generate_response,

                disease_info=disease_info,

                confidence=confidence,

                pest_info=pest_info,

                pest_confidence=pest_confidence,

                language=language,

            )

            except Exception as e:

                print(
                    f"[LLM WARNING] "
                    f"Advisory generation failed: {e}"
                )


        # ----------------------------------------------------
        # Safe fallback if LLM fails or confidence is low
        # ----------------------------------------------------

        if not advisory_text:

            mgmt = " ".join(
                disease_info.get(
                    "management",
                    []
                )
            )


            # ------------------------------------------------
            # Marathi
            # ------------------------------------------------

            if language == "mr":

                advisory_text = (

                    f"पिकावर "
                    f"{disease_info.get('name', disease_key)} "
                    f"रोगाची लक्षणे आढळली आहेत. "
                    f"व्यवस्थापन: {mgmt}"

                )


            # ------------------------------------------------
            # Hindi
            # ------------------------------------------------

            elif language == "hi":

                advisory_text = (

                    f"फसल पर "
                    f"{disease_info.get('name', disease_key)} "
                    f"के लक्षण पाए गए हैं। "
                    f"प्रबंधन: {mgmt}"

                )


            # ------------------------------------------------
            # English
            # ------------------------------------------------

            else:

                advisory_text = (

                    f"Symptoms of "
                    f"{disease_info.get('name', disease_key)} "
                    f"detected. "
                    f"Management: {mgmt}"

                )


        # ====================================================
        # 12. TEXT TO SPEECH
        # ====================================================

        audio_path_local = None


        if voice_service_loaded:

            try:

                audio_path_local = (
                    await asyncio.to_thread(

                        generate_regional_audio,

                        text_to_speak=advisory_text,

                        language=language,

                    )
                )

            except Exception as e:

                print(
                    f"[AUDIO WARNING] "
                    f"Voice synthesis skipped: {e}"
                )


        return (
            advisory_text,
            audio_path_local
        )


    # ========================================================
    # 13. RUN IMAGE UPLOAD AND ADVISORY IN PARALLEL
    # ========================================================

    cloud_url, (
        advisory_response,
        audio_path
    ) = await asyncio.gather(

        _upload_image(),

        _build_advisory()

    )


    # ========================================================
    # 14. HANDLE IMAGE URL
    # ========================================================

    if cloud_url:

        image_url = cloud_url

    else:

        # ----------------------------------------------------
        # Save image locally as fallback
        # ----------------------------------------------------

        file_ext = (

            image.filename.split(".")[-1]

            if image.filename
            and "." in image.filename

            else "jpg"

        )


        image_filename = (
            f"{case_id}.{file_ext}"
        )


        image_disk_path = os.path.join(
            UPLOAD_DIR,
            image_filename
        )


        try:

            with open(
                image_disk_path,
                "wb"
            ) as f:

                f.write(
                    image_bytes
                )

        except Exception as e:

            print(
                f"[IMAGE SAVE WARNING] "
                f"Could not write image to disk: {e}"
            )


        image_url = (
            "http://192.168.137.1:8000/"
            f"uploads/{image_filename}"
        )


    # ========================================================
    # 15. LOOK UP DISTRICT COORDINATES
    # ========================================================

    normalized_district = (
        district.strip().lower()
    )


    lat, lon = DISTRICT_COORDINATES.get(
        normalized_district,
        (
            20.3888,
            78.1204
        )
    )


    # ========================================================
    # 16. SAVE CASE TO DATABASE
    # ========================================================

    db_saved = True

    db_error = None


    try:

        new_case = Case(
        case_id=case_id,

            farmer_id=farmer_id,
        farmer_name=farmer_name,

        district=district,

        crop=crop_detected,

        # ----------------------------
        # Disease prediction
        # ----------------------------

        disease_detected=disease_key,
        confidence=confidence,

        # ----------------------------
        # Pest prediction
        # ----------------------------

        pest_detected=pest_key,
        pest_confidence=pest_confidence,
        pest_status=pest_status,

        # ----------------------------
        # Other information
        # ----------------------------

        severity=severity,

        latitude=lat,
        longitude=lon,

        image_url=image_url,

        status="Pending Expert"
    )


        db.add(
            new_case
        )

        db.commit()


    except Exception as e:

        db.rollback()

        db_saved = False

        db_error = str(e)


        print(
            f"[DB ERROR] "
            f"Failed to record case "
            f"{case_id} to Cloud DB: {e}"
        )


        print(
            traceback.format_exc()
        )


    # ========================================================
    # 17. RETURN FINAL API RESPONSE
    # ========================================================

    return PredictionResponse(

        # ----------------------------------------------------
        # Case
        # ----------------------------------------------------

        case_id=case_id,


        # ----------------------------------------------------
        # Crop
        # ----------------------------------------------------

        crop=crop_detected,


        # ----------------------------------------------------
        # Disease
        # ----------------------------------------------------

        disease=disease_key,

        confidence=confidence,


        # ----------------------------------------------------
        # Pest
        # ----------------------------------------------------

        pest=pest_key,

        pest_confidence=pest_confidence,

        pest_status=pest_status,

        pest_top_3=pest_top_3,


        # ----------------------------------------------------
        # Existing advisory/status fields
        # ----------------------------------------------------

        status="Pending Expert",

        response=advisory_response,

        language=language,

        audio_url=audio_path,


        # ----------------------------------------------------
        # Database status
        # ----------------------------------------------------

        db_saved=db_saved,

        db_error=db_error,

    )