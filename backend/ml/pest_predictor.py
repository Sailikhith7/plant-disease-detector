import json
import io
import os

import numpy as np
from PIL import Image


# ============================================================
# PATHS & CONFIG
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "weights",
    "pest_classifier_v1.tflite"
)

LABELS_PATH = os.path.join(
    BASE_DIR,
    "pest_labels.json"
)

CONFIDENCE_THRESHOLD = 0.70


# ============================================================
# LOAD LABELS
# ============================================================

with open(LABELS_PATH, "r", encoding="utf-8") as f:
    labels_data = json.load(f)

if isinstance(labels_data, dict):
    CLASS_NAMES = [
        labels_data[str(i)]
        for i in range(len(labels_data))
    ]
else:
    CLASS_NAMES = labels_data


# ============================================================
# LOAD TFLITE INTERPRETER
# ============================================================

try:
    from ai_edge_litert.interpreter import Interpreter

except ImportError:
    try:
        from tflite_runtime.interpreter import Interpreter

    except ImportError:
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter


interpreter = Interpreter(
    model_path=MODEL_PATH
)

interpreter.allocate_tensors()

INPUT_DETAILS = interpreter.get_input_details()
OUTPUT_DETAILS = interpreter.get_output_details()

INPUT_INDEX = INPUT_DETAILS[0]["index"]
OUTPUT_INDEX = OUTPUT_DETAILS[0]["index"]

INPUT_SHAPE = INPUT_DETAILS[0]["shape"]
INPUT_DTYPE = INPUT_DETAILS[0]["dtype"]


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image: Image.Image) -> np.ndarray:

    image = image.convert("RGB")

    # --------------------------------------------------------
    # Determine input layout
    # --------------------------------------------------------

    if INPUT_SHAPE[1] == 3:
        # NCHW
        target_h = int(INPUT_SHAPE[2])
        target_w = int(INPUT_SHAPE[3])
    else:
        # NHWC
        target_h = int(INPUT_SHAPE[1])
        target_w = int(INPUT_SHAPE[2])

    # --------------------------------------------------------
    # Center crop to square
    # --------------------------------------------------------

    w, h = image.size
    min_dim = min(w, h)

    left = (w - min_dim) / 2
    top = (h - min_dim) / 2
    right = (w + min_dim) / 2
    bottom = (h + min_dim) / 2

    image = image.crop(
        (left, top, right, bottom)
    )

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    image = image.resize(
        (target_w, target_h),
        Image.Resampling.BILINEAR
    )

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    img_array = np.asarray(
        image,
        dtype=np.float32
    ) / 255.0

    # --------------------------------------------------------
    # NHWC → NCHW if necessary
    # --------------------------------------------------------

    if INPUT_SHAPE[1] == 3:

        img_array = np.transpose(
            img_array,
            (2, 0, 1)
        )

    # --------------------------------------------------------
    # Add batch dimension
    # --------------------------------------------------------

    img_tensor = np.expand_dims(
        img_array,
        axis=0
    )

    return img_tensor.astype(INPUT_DTYPE)


# ============================================================
# SOFTMAX
# ============================================================

def softmax(logits):

    logits = np.asarray(
        logits,
        dtype=np.float64
    )

    logits -= np.max(logits)

    exp_values = np.exp(logits)

    return (
        exp_values /
        np.sum(exp_values)
    ).astype(np.float32)


# ============================================================
# PREDICT
# ============================================================

def predict(image_bytes: bytes) -> dict:

    # --------------------------------------------------------
    # Load image
    # --------------------------------------------------------

    image = Image.open(
        io.BytesIO(image_bytes)
    )

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    input_tensor = preprocess_image(image)

    # --------------------------------------------------------
    # Inference
    # --------------------------------------------------------

    interpreter.set_tensor(
        INPUT_INDEX,
        input_tensor
    )

    interpreter.invoke()

    # --------------------------------------------------------
    # Get output
    # --------------------------------------------------------

    raw_output = interpreter.get_tensor(
        OUTPUT_INDEX
    )[0]

    # --------------------------------------------------------
    # Dequantization
    # --------------------------------------------------------

    if OUTPUT_DETAILS[0]["dtype"] in [
        np.uint8,
        np.int8
    ]:

        scale, zero_point = (
            OUTPUT_DETAILS[0]["quantization"]
        )

        if scale > 0:

            raw_output = (
                scale *
                (
                    raw_output.astype(
                        np.float32
                    )
                    - zero_point
                )
            )

    # --------------------------------------------------------
    # Convert logits to probabilities
    # --------------------------------------------------------

    probabilities = softmax(
        raw_output
    )

    # --------------------------------------------------------
    # Top 3 predictions
    # --------------------------------------------------------

    top_indices = np.argsort(
        probabilities
    )[::-1][:3]

    top_predictions = [

        {
            "pest": CLASS_NAMES[idx],
            "confidence": float(
                probabilities[idx]
            )
        }

        for idx in top_indices
    ]

    # --------------------------------------------------------
    # Best prediction
    # --------------------------------------------------------

    best_index = int(
        top_indices[0]
    )

    best_pest = CLASS_NAMES[
        best_index
    ]

    best_confidence = float(
        probabilities[best_index]
    )

    # --------------------------------------------------------
    # Confidence status
    # --------------------------------------------------------

    if best_confidence >= CONFIDENCE_THRESHOLD:
        status = "confident"
    else:
        status = "uncertain"

    # --------------------------------------------------------
    # Diagnostic output
    # --------------------------------------------------------

    print(
        "--- PEST PREDICTION ---"
    )

    print(
        f"Pest: {best_pest}"
    )

    print(
        f"Confidence: "
        f"{best_confidence * 100:.2f}%"
    )

    print(
        f"Status: {status}"
    )

    print(
        "-----------------------"
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "pest": best_pest,

        "confidence": best_confidence,

        "status": status,

        "top_3": top_predictions
    }