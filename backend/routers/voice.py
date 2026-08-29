from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.voice_service import generate_regional_audio

router = APIRouter(prefix="/api/voice", tags=["Voice Advisory"])

class VoiceRequest(BaseModel):
    disease: str
    custom_advice: Optional[str] = None

class VoiceResponse(BaseModel):
    status: str
    disease: str
    advice_marathi: str
    audio_url: str

@router.post("/generate", response_model=VoiceResponse)
def get_voice_advisory(payload: VoiceRequest):
    audio_path, spoken_text = generate_regional_audio(payload.disease, payload.custom_advice)
    return VoiceResponse(
        status="SUCCESS",
        disease=payload.disease,
        advice_marathi=spoken_text,
        audio_url=audio_path
    )