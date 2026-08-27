import json
from pathlib import Path


# Path to the knowledge base
KNOWLEDGE_BASE_PATH = (
    Path(__file__).parent / "knowledge" / "diseases.json"
)


def load_knowledge_base():
    """Load disease information from diseases.json."""

    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_disease_information(disease_key):
    """
    Retrieve information for a classifier disease label.

    Example:
        get_disease_information("rice_leaf_blast")
    """

    knowledge_base = load_knowledge_base()

    disease = knowledge_base.get(disease_key)

    if disease is None:
        return None

    return disease


if __name__ == "__main__":

    # Test retrieval
    test_disease = "rice_leaf_blast"

    result = get_disease_information(test_disease)

    if result:
        print("Disease found!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Disease not found!")