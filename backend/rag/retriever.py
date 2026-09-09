import json
from pathlib import Path


# ============================================================
# KNOWLEDGE BASE PATHS
# ============================================================

BASE_DIR = Path(__file__).parent

DISEASE_KNOWLEDGE_BASE_PATH = (
    BASE_DIR / "knowledge" / "diseases.json"
)

PEST_KNOWLEDGE_BASE_PATH = (
    BASE_DIR / "knowledge" / "pests.json"
)


# ============================================================
# LOAD DISEASE KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():

    with open(
        DISEASE_KNOWLEDGE_BASE_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# LOAD PEST KNOWLEDGE BASE
# ============================================================

def load_pest_knowledge_base():

    with open(
        PEST_KNOWLEDGE_BASE_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# GET DISEASE INFORMATION
# ============================================================

def get_disease_information(disease_key):

    knowledge_base = load_knowledge_base()

    disease = knowledge_base.get(
        disease_key
    )

    return disease


# ============================================================
# GET PEST INFORMATION
# ============================================================

def get_pest_information(pest_key):

    try:

        knowledge_base = load_pest_knowledge_base()

    except FileNotFoundError:

        print(
            "[RAG WARNING] pests.json not found."
        )

        return None

    pest = knowledge_base.get(
        pest_key
    )

    if pest is None:

        print(
            f"[RAG WARNING] No information found "
            f"for pest: {pest_key}"
        )

    return pest


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_disease = "rice_leaf_blast"

    result = get_disease_information(
        test_disease
    )

    if result:

        print("Disease found!")

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            )
        )

    else:

        print("Disease not found!")


    test_pest = "Rice_Yellow_Borer"

    pest_result = get_pest_information(
        test_pest
    )

    if pest_result:

        print("Pest found!")

        print(
            json.dumps(
                pest_result,
                indent=2,
                ensure_ascii=False
            )
        )

    else:

        print("Pest information not found!")