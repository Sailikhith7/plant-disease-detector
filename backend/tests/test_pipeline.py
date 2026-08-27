from pathlib import Path

from backend.ml.predictor import predict
from backend.rag.retriever import get_disease_information
from backend.rag.llm import generate_response


# =========================================================
# CONFIGURATION
# =========================================================

IMAGE_PATH = Path(r"C:\Plant Detector\test_images\download.jpg")

# Choose:
# "en" = English
# "mr" = Marathi
# "hi" = Hindi

LANGUAGE = "en"

# Recommended confidence threshold
CONFIDENCE_THRESHOLD = 0.85


# =========================================================
# 1. LOAD IMAGE
# =========================================================

if not IMAGE_PATH.exists():
    raise FileNotFoundError(
        f"Image not found: {IMAGE_PATH}"
    )


with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()


# =========================================================
# 2. ML PREDICTION
# =========================================================

prediction = predict(image_bytes)


print("\n========================================")
print("ML PREDICTION")
print("========================================")

print(f"Crop:       {prediction['crop']}")
print(f"Disease:    {prediction['disease']}")
print(f"Confidence: {prediction['confidence']:.2%}")
print(f"Status:     {prediction['status']}")


# =========================================================
# 3. EXTRACT PREDICTION
# =========================================================

disease_key = prediction["disease"]
confidence = prediction["confidence"]


# =========================================================
# 4. CONFIDENCE CHECK
# =========================================================

if confidence < CONFIDENCE_THRESHOLD:

    print("\n========================================")
    print("UNCERTAIN PREDICTION")
    print("========================================")

    print(
        f"The model confidence is {confidence:.2%}, "
        f"which is below the recommended "
        f"threshold of {CONFIDENCE_THRESHOLD:.0%}."
    )

    print(
        f"Top prediction: {disease_key}"
    )

    print(
        "\nThe prediction will still be passed "
        "to the RAG + LLM system, but the final "
        "response will clearly indicate uncertainty."
    )


# =========================================================
# 5. RETRIEVE KNOWLEDGE
# =========================================================

disease_info = get_disease_information(
    disease_key
)


if disease_info is None:

    print("\nNo information was found in the "
          "knowledge base for this disease.")

    print(
        "The system cannot generate reliable "
        "agricultural guidance."
    )

    raise SystemExit(1)


print("\n========================================")
print("RAG RETRIEVAL")
print("========================================")

print(
    f"Knowledge retrieved for: "
    f"{disease_info['name']}"
)


# =========================================================
# 6. GENERATE LLM RESPONSE
# =========================================================

print("\n========================================")
print("GENERATING AI RESPONSE")
print("========================================")

response = generate_response(
    disease_info=disease_info,
    confidence=confidence,
    language=LANGUAGE
)


# =========================================================
# 7. FINAL RESPONSE
# =========================================================

print("\n========================================")
print("FINAL AGRICULTURAL GUIDANCE")
print("========================================\n")

print(response)

print("\n========================================")
print("PIPELINE COMPLETE")
print("========================================")