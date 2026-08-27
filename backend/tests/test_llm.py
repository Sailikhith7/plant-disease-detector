from backend.rag.retriever import get_disease_information
from backend.rag.llm import generate_response


# -----------------------------------------
# Test disease
# -----------------------------------------

DISEASE_KEY = "cotton_curl_virus"

CONFIDENCE = 0.9999


# -----------------------------------------
# Retrieve disease information
# -----------------------------------------

disease_info = get_disease_information(
    DISEASE_KEY
)


if disease_info is None:
    raise RuntimeError(
        f"Disease '{DISEASE_KEY}' "
        "was not found in diseases.json"
    )


# -----------------------------------------
# Generate response
# -----------------------------------------

response = generate_response(
    disease_info=disease_info,
    confidence=CONFIDENCE,
    language="hi"
)


# -----------------------------------------
# Display result
# -----------------------------------------

print("\n================================")
print("OLLAMA LLM RESPONSE")
print("================================\n")

print(response)