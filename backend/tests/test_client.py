import requests


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000/api/predict"

IMAGE_PATH = r"C:\Plant Detector\test_images\download.jpg"

LANGUAGE = "mr"
# en = English
# mr = Marathi
# hi = Hindi


# =========================================================
# SEND IMAGE TO API
# =========================================================

with open(IMAGE_PATH, "rb") as image_file:

    files = {
        "image": (
            "image.jpg",
            image_file,
            "image/jpeg"
        )
    }

    data = {
        "language": LANGUAGE
    }

    response = requests.post(
        API_URL,
        files=files,
        data=data
    )


# =========================================================
# DISPLAY RESULT
# =========================================================

print("\n========================================")
print("API RESPONSE")
print("========================================")

print("HTTP Status:", response.status_code)

print("\nResponse:")

try:
    result = response.json()

    print("\nCrop:")
    print(result.get("crop"))

    print("\nDisease:")
    print(result.get("disease"))

    print("\nConfidence:")
    print(result.get("confidence"))

    print("\nStatus:")
    print(result.get("status"))

    print("\nLanguage:")
    print(result.get("language"))

    print("\nAI Guidance:")
    print(result.get("response"))

except Exception:
    print(response.text)