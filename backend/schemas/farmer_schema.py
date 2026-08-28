from pydantic import BaseModel


class FarmerCreate(BaseModel):
    farmer_id: str
    full_name: str
    phone_number: str
    district: str
    taluka: str
    primary_crop: str
    telegram_chat_id: str


class FarmerResponse(BaseModel):
    id: int
    farmer_id: str
    full_name: str
    phone_number: str
    district: str
    taluka: str
    primary_crop: str
    telegram_chat_id: str




class FarmerCreate(BaseModel):
    farmer_id: str
    full_name: str
    phone_number: str
    district: str
    taluka: str
    primary_crop: str
    telegram_chat_id: str


class FarmerResponse(BaseModel):
    id: int
    farmer_id: str
    full_name: str
    phone_number: str
    district: str
    taluka: str
    primary_crop: str
    telegram_chat_id: str