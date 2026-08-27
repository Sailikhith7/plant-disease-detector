import json
import io
import os

import numpy as np
from PIL import Image


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "weights",
    "crop_classifier_v1.tflite"
)

LABELS_PATH = os.path.join(
    BASE_DIR,
    "labels.json"
)

CALIBRATION_PATH = os.path.join(
    BASE_DIR,
    "calibration.json"
)


# ============================================================
# LOAD LABELS
# ============================================================

with open(LABELS_PATH, "r") as f:
    labels_data = json.load(f)


# Support either:
# {
#     "0": "cotton_bacterial_blight",
#     ...
# }
#
# or:
# [
#     "cotton_bacterial_blight",
#     ...
# ]

if isinstance(labels_data, dict):

    CLASS_NAMES = [
        labels_data[str(i)]
        for i in range(len(labels_data))
    ]

else:

    CLASS_NAMES = labels_data


# ============================================================
# LOAD CALIBRATION
# ============================================================

with open(CALIBRATION_PATH, "r") as f:
    calibration = json.load(f)


TEMPERATURE = float(
    calibration["temperature"]
)

CONFIDENCE_THRESHOLD = float(
    calibration["confidence_threshold"]
)


# ============================================================
# LOAD TFLITE INTERPRETER
# ============================================================

try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    from tflite_runtime.interpreter import Interpreter


interpreter = Interpreter(
    model_path=MODEL_PATH
)

interpreter.allocate_tensors()


INPUT_DETAILS = interpreter.get_input_details()
OUTPUT_DETAILS = interpreter.get_output_details()

INPUT_INDEX = INPUT_DETAILS[0]["index"]
OUTPUT_INDEX = OUTPUT_DETAILS[0]["index"]


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

IMAGENET_MEAN = np.array(
    [0.485, 0.456, 0.406],
    dtype=np.float32
)

IMAGENET_STD = np.array(
    [0.229, 0.224, 0.225],
    dtype=np.float32
)


def preprocess_image(image):
    """
    Preprocess a PIL image using the exact
    validation/test preprocessing used during training.
    """

    image = image.convert("RGB")

    image = image.resize(
        (224, 224)
    )

    image = np.asarray(
        image,
        dtype=np.float32
    )

    # Convert [0, 255] -> [0, 1]
    image = image / 255.0

    # ImageNet normalization
    image = (
        image - IMAGENET_MEAN
    ) / IMAGENET_STD

    # HWC -> CHW
    image = np.transpose(
        image,
        (2, 0, 1)
    )

    # Add batch dimension
    image = np.expand_dims(
        image,
        axis=0
    )

    return image.astype(
        np.float32
    )


# ============================================================
# SOFTMAX
# ============================================================

def softmax(logits):
    """
    Numerically stable softmax.
    """

    logits = logits - np.max(
        logits
    )

    exp_values = np.exp(logits)

    return (
        exp_values /
        np.sum(exp_values)
    )


# ============================================================
# PREDICT
# ============================================================

def predict(image_bytes):
    """
    Run disease classification.

    Parameters
    ----------
    image_bytes : bytes
        Raw image bytes.

    Returns
    -------
    dict
        Prediction result containing crop,
        disease, confidence, status and top-3.
    """

    # --------------------------------------------------------
    # Load image
    # --------------------------------------------------------

    image = Image.open(
        io.BytesIO(image_bytes)
    )

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    input_tensor = preprocess_image(
        image
    )

    # --------------------------------------------------------
    # TFLite inference
    # --------------------------------------------------------

    interpreter.set_tensor(
        INPUT_INDEX,
        input_tensor
    )

    interpreter.invoke()

    logits = interpreter.get_tensor(
        OUTPUT_INDEX
    )[0]

    # --------------------------------------------------------
    # Temperature scaling
    # --------------------------------------------------------

    calibrated_logits = (
        logits / TEMPERATURE
    )

    probabilities = softmax(
        calibrated_logits
    )

    # --------------------------------------------------------
    # Top-3 predictions
    # --------------------------------------------------------

    top_indices = np.argsort(
        probabilities
    )[::-1][:3]

    top_predictions = []

    for index in top_indices:

        top_predictions.append({
            "disease": CLASS_NAMES[index],
            "confidence": float(
                probabilities[index]
            )
        })

    # --------------------------------------------------------
    # Best prediction
    # --------------------------------------------------------

    best_index = top_indices[0]

    best_disease = CLASS_NAMES[
        best_index
    ]

    best_confidence = float(
        probabilities[best_index]
    )

    # --------------------------------------------------------
    # Determine crop
    # --------------------------------------------------------

    crop = best_disease.split(
        "_"
    )[0]

    # --------------------------------------------------------
    # Confidence decision
    # --------------------------------------------------------

    if (
        best_confidence
        >= CONFIDENCE_THRESHOLD
    ):

        status = "confident"

    else:

        status = "uncertain"

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "crop": crop,
        "disease": best_disease,
        "confidence": best_confidence,
        "status": status,
        "top_3": top_predictions
    }