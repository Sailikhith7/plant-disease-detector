from pydantic import BaseModel


class PredictionResponse(BaseModel):
    crop: str
    disease: str
    confidence: float
    status: str
    response: str
    language: str