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

OLLAMA_API_URL = "https://ollama.com/api/chat"


if not OLLAMA_API_KEY:
    raise RuntimeError(
        "OLLAMA_API_KEY is not set. "
        "Please check your .env file."
    )


LANGUAGES = {
    "en": "English",
    "mr": "Marathi",
    "hi": "Hindi"
}


def generate_response(
    disease_info,
    confidence,
    language="en"
):
    """
    Generate a farmer-friendly response using
    Ollama Cloud and information retrieved
    from the local knowledge base.
    """

    # -----------------------------------------
    # Validate language
    # -----------------------------------------

    if language not in LANGUAGES:
        raise ValueError(
            "Unsupported language. "
            "Use 'en', 'mr', or 'hi'."
        )

    language_name = LANGUAGES[language]


    # -----------------------------------------
    # Prepare retrieved knowledge
    # -----------------------------------------

    symptoms = "\n".join(
        f"- {item}"
        for item in disease_info["symptoms"]
    )

    causes = "\n".join(
        f"- {item}"
        for item in disease_info["causes"]
    )

    favorable_conditions = "\n".join(
        f"- {item}"
        for item in disease_info["favorable_conditions"]
    )

    prevention = "\n".join(
        f"- {item}"
        for item in disease_info["prevention"]
    )

    management = "\n".join(
        f"- {item}"
        for item in disease_info["management"]
    )


    # -----------------------------------------
    # Confidence description
    # -----------------------------------------

    if confidence >= 0.85:
        confidence_instruction = (
            "The classifier confidence is high. "
            "Present the predicted disease as the "
            "likely identification, while avoiding "
            "absolute certainty."
        )
    else:
        confidence_instruction = (
            "The classifier confidence is below the "
            "recommended system threshold of 85%. Clearly "
            "tell the user that this is an uncertain "
            "prediction and should not be treated as a "
            "confirmed diagnosis."
        )


    # -----------------------------------------
    # Build prompt
    # -----------------------------------------

    prompt = f"""
You are an agricultural disease information assistant.

The crop image was analyzed by a computer vision
classifier.

CROP:
{disease_info["crop"]}

PREDICTED DISEASE:
{disease_info["name"]}

CLASSIFIER CONFIDENCE:
{confidence:.2%}

CONFIDENCE INSTRUCTION:
{confidence_instruction}


VERIFIED KNOWLEDGE BASE INFORMATION
------------------------------------

DESCRIPTION:
{disease_info["description"]}


SYMPTOMS:
{symptoms}


CAUSES:
{causes}


FAVORABLE CONDITIONS:
{favorable_conditions}


PREVENTION:
{prevention}


MANAGEMENT:
{management}


TASK
----

Generate a clear and useful explanation for a farmer.

The entire response MUST be written in:
{language_name}

Use this structure:

1. Disease identified
2. What it is
3. Symptoms
4. Causes
5. What to do
6. Prevention


IMPORTANT RULES
---------------

- Use the provided knowledge-base information
  as the source for disease-specific facts.

- Do not invent disease information.

- Do not invent pesticide names.

- Do not invent pesticide doses.

- Do not invent treatment methods that are not
  present in the provided information.

- Do not claim that the image provides a certain
  diagnosis.

- If the confidence is low, clearly communicate
  that the prediction is uncertain.

- Keep the explanation practical and easy for
  a farmer to understand.

- Do not mention RAG, embeddings, APIs, prompts,
  MobileNet, Python, or internal software.

- Do not include information unrelated to the
  detected crop disease.

- The final response must be entirely in
  {language_name}.
"""


    # -----------------------------------------
    # Call Ollama Cloud
    # -----------------------------------------

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
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


    response = requests.post(
        OLLAMA_API_URL,
        headers=headers,
        json=payload,
        timeout=120
    )


    # -----------------------------------------
    # Handle API errors
    # -----------------------------------------

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama API error "
            f"{response.status_code}: "
            f"{response.text}"
        )


    result = response.json()


    # -----------------------------------------
    # Return generated text
    # -----------------------------------------

    return result["message"]["content"]