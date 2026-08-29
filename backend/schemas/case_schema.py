from pydantic import BaseModel
from typing import Optional

class PredictionResponse(BaseModel):
    case_id: Optional[str] = None
    crop: str
    disease: str
    confidence: float
    status: str
    response: str
    language: str = "en"
    audio_url: Optional[str] = None