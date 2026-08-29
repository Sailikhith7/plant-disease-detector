import os
import hashlib
from gtts import gTTS

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_regional_audio(text_to_speak: str, language: str = "mr"):
    if not text_to_speak or not text_to_speak.strip():
        text_to_speak = "पिकाची तपासणी पूर्ण झाली आहे. योग्य कृषी सल्ला पाळा."

    # Language mapping
    target_lang = "mr" if language == "mr" else ("hi" if language == "hi" else "en")

    text_hash = hashlib.md5((text_to_speak + target_lang).encode("utf-8")).hexdigest()[:12]
    filename = f"advisory_{target_lang}_{text_hash}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    if not os.path.exists(filepath):
        tts = gTTS(text=text_to_speak, lang=target_lang, slow=False)
        tts.save(filepath)

    return f"/static/audio/{filename}"