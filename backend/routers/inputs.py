from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.ml.predictor import predict
from backend.rag.retriever import get_disease_information
from backend.rag.llm import generate_response

from backend.schemas.case_schema import PredictionResponse


router = APIRouter(
    prefix="/api",
    tags=["Plant Disease Detection"]
)


CONFIDENCE_THRESHOLD = 0.85

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png"
}


@router.post(
    "/predict",
    response_model=PredictionResponse
)
async def predict_disease(
    image: UploadFile = File(...),
    language: str = Form("en")
):

    # =====================================================
    # 1. Validate language
    # =====================================================

    if language not in ["en", "mr", "hi"]:
        raise HTTPException(
            status_code=400,
            detail="Language must be en, mr, or hi."
        )


    # =====================================================
    # 2. Validate image type
    # =====================================================

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image type. "
                "Only JPG, JPEG and PNG images are allowed."
            )
        )


    # =====================================================
    # 3. Read image
    # =====================================================

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


    # =====================================================
    # 4. ML prediction
    # =====================================================

    try:
        prediction = predict(image_bytes)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ML prediction failed: {str(e)}"
        )


    disease_key = prediction["disease"]
    confidence = prediction["confidence"]


    # =====================================================
    # 5. RAG retrieval
    # =====================================================

    disease_info = get_disease_information(
        disease_key
    )


    if disease_info is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No knowledge-base information "
                f"found for disease: {disease_key}"
            )
        )


    # =====================================================
    # 6. LLM generation
    # =====================================================

    try:

        response = generate_response(
            disease_info=disease_info,
            confidence=confidence,
            language=language
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"LLM generation failed: {str(e)}"
        )


    # =====================================================
    # 7. Return response
    # =====================================================

    return PredictionResponse(
    crop=prediction["crop"],
    disease=disease_key,
    confidence=confidence,
    status=prediction["status"],
    response=response,
    language=language
)