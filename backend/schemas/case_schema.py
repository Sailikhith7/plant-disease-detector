from pydantic import BaseModel

from typing import Optional


class PredictionResponse(BaseModel):

    case_id: Optional[str] = None

    crop: str

    disease: str

    confidence: float

    # ========================================================
    # PEST INFORMATION
    # ========================================================

    pest: Optional[str] = None

    pest_confidence: Optional[float] = None

    pest_status: Optional[str] = None

    # ========================================================
    # GENERAL RESPONSE
    # ========================================================

    status: str

    response: str

    language: str = "en"

    audio_url: Optional[str] = None

    db_saved: bool = True

    db_error: Optional[str] = None