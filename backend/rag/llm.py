import os
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")
load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "https://ollama.com/api/chat")

LANGUAGES = {
    "en": "English",
    "mr": "Marathi (मराठी)",
    "hi": "Hindi (हिंदी)"
}

def generate_response(disease_info: dict, confidence: float, language: str = "mr") -> str:
    language_name = LANGUAGES.get(language, "Marathi (मराठी)")
    
    symptoms = "\n".join(f"- {item}" for item in disease_info.get("symptoms", []))
    causes = "\n".join(f"- {item}" for item in disease_info.get("causes", []))
    favorable_conditions = "\n".join(f"- {item}" for item in disease_info.get("favorable_conditions", []))
    prevention = "\n".join(f"- {item}" for item in disease_info.get("prevention", []))
    management = "\n".join(f"- {item}" for item in disease_info.get("management", []))

    language_constraint = (
        "Do NOT write any English sentences or alphabets."
        if language != "en"
        else "Write only in English — do not switch to or mix in Marathi, Hindi, or any other language."
    )

    prompt = f"""
You are an expert agricultural assistant.
A farmer has submitted a crop leaf photo.

CROP: {disease_info.get('crop', '')}
DISEASE: {disease_info.get('name', '')}
CONFIDENCE: {confidence:.2%}

SYMPTOMS:
{symptoms}

MANAGEMENT:
{management}

PREVENTION:
{prevention}

TASK:
Provide a clear, 3-4 line practical diagnosis and treatment advice for the farmer.
STRICT INSTRUCTION: The ENTIRE response MUST be written in {language_name}.
{language_constraint}
"""

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()["message"]["content"].strip()
    except Exception as e:
        print(f"Ollama API Error: {e}")

    # Safe fallback if the API drops — kept in the SAME language that was
    # requested, not hardcoded to Marathi, so an API failure on an English
    # or Hindi request doesn't silently hand back Marathi text (and audio).
    fallback_by_language = {
        "en": f"Symptoms of {disease_info.get('name')} have been detected on the crop. Management: {management}",
        "hi": f"फसल पर {disease_info.get('name')} के लक्षण दिखाई दिए हैं। प्रबंधन: {management}",
        "mr": f"पिकावर {disease_info.get('name')} ची लक्षणे आढळली आहेत. नियंत्रणासाठी: {management}",
    }
    return fallback_by_language.get(language, fallback_by_language["mr"])