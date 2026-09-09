import os

import requests

from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ROOT_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(
    BASE_DIR / ".env"
)

load_dotenv(
    ROOT_DIR / ".env"
)

load_dotenv()


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gpt-oss:20b-cloud"
)

OLLAMA_API_URL = os.getenv(
    "OLLAMA_API_URL",
    "https://ollama.com/api/chat"
)


# ============================================================
# LANGUAGES
# ============================================================

LANGUAGES = {

    "en": "English",

    "mr": "Marathi (मराठी)",

    "hi": "Hindi (हिंदी)"
}


# ============================================================
# GENERATE COMBINED ADVISORY
# ============================================================

def generate_response(
    disease_info: dict | None,
    confidence: float,
    language: str = "mr",
    pest_info: dict | None = None,
    pest_confidence: float = 0.0
) -> str:

    language_name = LANGUAGES.get(
        language,
        "Marathi (मराठी)"
    )


    # ========================================================
    # DISEASE INFORMATION
    # ========================================================

    disease_name = "Not available"

    disease_crop = ""

    symptoms = ""

    causes = ""

    favorable_conditions = ""

    prevention = ""

    management = ""


    if disease_info:

        disease_name = disease_info.get(
            "name",
            "Unknown disease"
        )

        disease_crop = disease_info.get(
            "crop",
            ""
        )

        symptoms = "\n".join(
            f"- {item}"
            for item in disease_info.get(
                "symptoms",
                []
            )
        )

        causes = "\n".join(
            f"- {item}"
            for item in disease_info.get(
                "causes",
                []
            )
        )

        favorable_conditions = "\n".join(
            f"- {item}"
            for item in disease_info.get(
                "favorable_conditions",
                []
            )
        )

        prevention = "\n".join(
            f"- {item}"
            for item in disease_info.get(
                "prevention",
                []
            )
        )

        management = "\n".join(
            f"- {item}"
            for item in disease_info.get(
                "management",
                []
            )
        )


    # ========================================================
    # PEST INFORMATION
    # ========================================================

    pest_name = "No pest information available"

    pest_crop = ""

    pest_symptoms = ""

    pest_causes = ""

    pest_favorable_conditions = ""

    pest_prevention = ""

    pest_management = ""


    if pest_info:

        pest_name = pest_info.get(
            "name",
            "Unknown pest"
        )

        pest_crop = pest_info.get(
            "crop",
            ""
        )

        pest_symptoms = "\n".join(
            f"- {item}"
            for item in pest_info.get(
                "symptoms",
                []
            )
        )

        pest_causes = "\n".join(
            f"- {item}"
            for item in pest_info.get(
                "causes",
                []
            )
        )

        pest_favorable_conditions = "\n".join(
            f"- {item}"
            for item in pest_info.get(
                "favorable_conditions",
                []
            )
        )

        pest_prevention = "\n".join(
            f"- {item}"
            for item in pest_info.get(
                "prevention",
                []
            )
        )

        pest_management = "\n".join(
            f"- {item}"
            for item in pest_info.get(
                "management",
                []
            )
        )


    # ========================================================
    # LANGUAGE CONSTRAINT
    # ========================================================

    if language != "en":

        language_constraint = (
            "Do NOT write English sentences. "
            "Write the entire response only in "
            f"{language_name}."
        )

    else:

        language_constraint = (
            "Write only in English."
        )


    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are an expert agricultural assistant.

A farmer has submitted a crop leaf photo.

Your job is to provide a short, practical advisory based ONLY
on the verified information supplied below.

Do NOT invent pesticides, chemical names, dosages,
treatment schedules, or agricultural facts that are not
present in the supplied information.

============================================================
CROP
============================================================

{disease_crop or pest_crop}

============================================================
DISEASE DETECTION
============================================================

Disease:
{disease_name}

Disease confidence:
{confidence:.2%}

Disease symptoms:
{symptoms}

Disease causes:
{causes}

Disease favorable conditions:
{favorable_conditions}

Disease prevention:
{prevention}

Disease management:
{management}

============================================================
PEST DETECTION
============================================================

Pest:
{pest_name}

Pest confidence:
{pest_confidence:.2%}

Pest symptoms:
{pest_symptoms}

Pest causes:
{pest_causes}

Pest favorable conditions:
{pest_favorable_conditions}

Pest prevention:
{pest_prevention}

Pest management:
{pest_management}

============================================================
TASK
============================================================

Provide a concise 3-5 line practical advisory for the farmer.

If both a disease and pest are detected with useful confidence,
briefly mention both.

If pest information is unavailable, mention the detected pest
but clearly state that detailed pest management information is
not currently available.

If disease information is unavailable, do the same for the
disease.

Do not make up missing information.

Entire response must be written in {language_name}.

{language_constraint}
"""


    # ========================================================
    # API REQUEST
    # ========================================================

    headers = {

        "Authorization":
            f"Bearer {OLLAMA_API_KEY}",

        "Content-Type":
            "application/json"
    }


    payload = {

        "model": OLLAMA_MODEL,

        "messages": [

            {
                "role": "user",
                "content": prompt
            }

        ],

        "stream": False
    }


    # ========================================================
    # CALL OLLAMA
    # ========================================================

    try:

        response = requests.post(
            OLLAMA_API_URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        if response.status_code == 200:

            return (
                response.json()
                ["message"]
                ["content"]
                .strip()
            )

        print(
            f"[OLLAMA WARNING] "
            f"HTTP {response.status_code}: "
            f"{response.text}"
        )

    except Exception as e:

        print(
            f"[OLLAMA ERROR] {e}"
        )


    # ========================================================
    # SAFE FALLBACK
    # ========================================================

    if language == "mr":

        disease_text = (
            f"{disease_name} आढळला आहे."
            if disease_info
            else ""
        )

        pest_text = (
            f"कीड: {pest_name}."
            if pest_info
            else ""
        )

        management_text = (
            " ".join(
                disease_info.get(
                    "management",
                    []
                )
            )
            if disease_info
            else ""
        )

        pest_management_text = (
            " ".join(
                pest_info.get(
                    "management",
                    []
                )
            )
            if pest_info
            else
            "या किडीसाठी सविस्तर व्यवस्थापन माहिती उपलब्ध नाही."
        )

        return (
            f"{disease_text} "
            f"{pest_text} "
            f"व्यवस्थापन: {management_text} "
            f"{pest_management_text}"
        ).strip()


    if language == "hi":

        disease_text = (
            f"{disease_name} के लक्षण पाए गए हैं."
            if disease_info
            else ""
        )

        pest_text = (
            f"कीट: {pest_name}."
            if pest_info
            else ""
        )

        management_text = (
            " ".join(
                disease_info.get(
                    "management",
                    []
                )
            )
            if disease_info
            else ""
        )

        pest_management_text = (
            " ".join(
                pest_info.get(
                    "management",
                    []
                )
            )
            if pest_info
            else
            "इस कीट के लिए विस्तृत प्रबंधन जानकारी उपलब्ध नहीं है."
        )

        return (
            f"{disease_text} "
            f"{pest_text} "
            f"प्रबंधन: {management_text} "
            f"{pest_management_text}"
        ).strip()


    # English fallback

    disease_text = (
        f"Disease detected: {disease_name}."
        if disease_info
        else
        "No detailed disease information is available."
    )

    pest_text = (
        f"Pest detected: {pest_name}."
        if pest_info
        else
        "No pest information is available."
    )

    management_text = (
        " ".join(
            disease_info.get(
                "management",
                []
            )
        )
        if disease_info
        else
        "No disease management information is available."
    )

    pest_management_text = (
        " ".join(
            pest_info.get(
                "management",
                []
            )
        )
        if pest_info
        else
        "Detailed pest management information is not currently available."
    )

    return (
        f"{disease_text} "
        f"{pest_text} "
        f"Disease management: {management_text} "
        f"Pest management: {pest_management_text}"
    ).strip()