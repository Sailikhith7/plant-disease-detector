import json
import io
import os

import numpy as np
from PIL import Image


# ============================================================
# V5 PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "weights",
    "crop_classifier_v5.tflite"
)

LABELS_PATH = os.path.join(
    BASE_DIR,
    "labels_v5.json"
)

CALIBRATION_PATH = os.path.join(
    BASE_DIR,
    "calibration_v5.json"
)


# ============================================================
# VERIFY REQUIRED FILES
# ============================================================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"V5 model not found:\n{MODEL_PATH}"
    )

if not os.path.exists(LABELS_PATH):
    raise FileNotFoundError(
        f"V5 labels file not found:\n{LABELS_PATH}"
    )


# ============================================================
# LOAD V5 LABELS
# ============================================================

with open(LABELS_PATH, "r") as f:
    labels_data = json.load(f)


# Support either:
#
# {
#     "0": "cotton_bacterial_blight",
#     "1": "cotton_curl_virus",
#     ...
# }
#
# OR:
#
# [
#     "cotton_bacterial_blight",
#     "cotton_curl_virus",
#     ...
# ]

if isinstance(labels_data, dict):

    CLASS_NAMES = [
        labels_data[str(i)]
        for i in range(len(labels_data))
    ]

else:

    CLASS_NAMES = labels_data


NUM_CLASSES = len(CLASS_NAMES)


# ============================================================
# LOAD V5 CALIBRATION
# ============================================================

TEMPERATURE = 1.0

# V5 calibration file currently contains the temperature,
# but not a confidence threshold.
#
# Keep the existing backend behavior using 0.70 as the
# default threshold.

CONFIDENCE_THRESHOLD = 0.70


if os.path.exists(CALIBRATION_PATH):

    try:

        with open(CALIBRATION_PATH, "r") as f:
            calibration = json.load(f)

        TEMPERATURE = float(
            calibration.get("temperature", 1.0)
        )

        CONFIDENCE_THRESHOLD = float(
            calibration.get(
                "confidence_threshold",
                0.70
            )
        )

    except Exception as e:

        print(
            f"[WARN] Failed to read V5 calibration file: {e}"
        )


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

OUTPUT_SHAPE = OUTPUT_DETAILS[0]["shape"]
OUTPUT_DTYPE = OUTPUT_DETAILS[0]["dtype"]


# ============================================================
# STARTUP DIAGNOSTICS
# ============================================================

print("=" * 60)
print("V5 PREDICTOR INITIALIZED")
print("=" * 60)

print(f"Model       : {MODEL_PATH}")
print(f"Labels      : {LABELS_PATH}")
print(f"Calibration : {CALIBRATION_PATH}")

print(f"Classes     : {NUM_CLASSES}")

print(f"Input shape : {INPUT_SHAPE}")
print(f"Input dtype : {INPUT_DTYPE}")

print(f"Output shape: {OUTPUT_SHAPE}")
print(f"Output dtype: {OUTPUT_DTYPE}")

print(f"Temperature : {TEMPERATURE:.4f}")
print(
    f"Threshold   : {CONFIDENCE_THRESHOLD:.4f}"
)

print("=" * 60)


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Preprocess an image for the V5 MobileNetV3 model.

    V5 verified input:
        Shape : (1, 224, 224, 3)
        Dtype : float32
        Range : [0, 255]

    MobileNetV3 contains its own preprocessing,
    so the image must NOT be divided by 255 here.
    """

    # --------------------------------------------------------
    # Convert to RGB
    # --------------------------------------------------------

    image = image.convert("RGB")


    # --------------------------------------------------------
    # Determine expected image layout
    # --------------------------------------------------------

    if len(INPUT_SHAPE) != 4:
        raise ValueError(
            f"Unexpected V5 input shape: {INPUT_SHAPE}"
        )


    # NCHW: [batch, channels, height, width]
    if INPUT_SHAPE[1] == 3:

        target_h = int(INPUT_SHAPE[2])
        target_w = int(INPUT_SHAPE[3])

        nchw = True

    # NHWC: [batch, height, width, channels]
    else:

        target_h = int(INPUT_SHAPE[1])
        target_w = int(INPUT_SHAPE[2])

        nchw = False


    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    image = image.resize(
        (target_w, target_h)
    )


    # --------------------------------------------------------
    # Convert to NumPy
    # --------------------------------------------------------

    img_array = np.asarray(
        image,
        dtype=np.float32
    )


    # --------------------------------------------------------
    # V5 FLOAT32 preprocessing
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Do NOT do:
    #
    # img_array = img_array / 255.0
    #
    # V5 was verified using [0,255] input.
    # MobileNetV3's built-in preprocessing handles
    # normalization internally.
    # --------------------------------------------------------

    if INPUT_DTYPE == np.uint8:

        img_array = img_array.astype(
            np.uint8
        )

    else:

        img_array = img_array.astype(
            np.float32
        )


    # --------------------------------------------------------
    # Convert NHWC -> NCHW if required
    # --------------------------------------------------------

    if nchw:

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


    return img_tensor.astype(
        INPUT_DTYPE
    )


# ============================================================
# SOFTMAX
# ============================================================

def softmax(values):
    """
    Numerically stable softmax.
    """

    values = np.asarray(
        values,
        dtype=np.float64
    )

    values = values - np.max(values)

    exp_values = np.exp(values)

    probabilities = (
        exp_values /
        np.sum(exp_values)
    )

    return probabilities.astype(
        np.float32
    )


# ============================================================
# TEMPERATURE CALIBRATION
# ============================================================

def calibrate_probabilities(
    probabilities,
    temperature
):
    """
    Apply temperature scaling to an already-softmaxed
    probability vector.

    The V5 model output was verified to be probabilities:

        minimum >= 0
        maximum <= 1
        sum ~= 1

    Therefore, we first convert probabilities to
    log-probabilities and then apply temperature scaling.

    This is equivalent to applying temperature scaling
    to logits up to an additive constant.
    """

    probabilities = np.asarray(
        probabilities,
        dtype=np.float64
    )

    # Avoid log(0)
    probabilities = np.clip(
        probabilities,
        1e-12,
        1.0
    )

    # Convert probability space to logit-equivalent space
    log_probabilities = np.log(
        probabilities
    )

    # Temperature scaling
    calibrated_values = (
        log_probabilities /
        float(temperature)
    )

    # Convert back to probabilities
    calibrated_probabilities = softmax(
        calibrated_values
    )

    return calibrated_probabilities


# ============================================================
# HANDLE MODEL OUTPUT
# ============================================================

def process_model_output(raw_output):
    """
    Convert the raw TFLite output into probabilities.

    V5 currently produces a softmax probability vector.

    Also supports logits as a fallback.
    """

    raw_output = np.asarray(
        raw_output,
        dtype=np.float32
    )

    # --------------------------------------------------------
    # Detect whether output already looks like probabilities
    # --------------------------------------------------------

    is_non_negative = np.all(
        raw_output >= 0
    )

    output_sum = np.sum(
        raw_output
    )

    is_probability_vector = (
        is_non_negative
        and
        np.isclose(
            output_sum,
            1.0,
            atol=1e-3
        )
    )


    # --------------------------------------------------------
    # Already probabilities
    # --------------------------------------------------------

    if is_probability_vector:

        probabilities = raw_output

    # --------------------------------------------------------
    # Otherwise treat as logits
    # --------------------------------------------------------

    else:

        probabilities = softmax(
            raw_output
        )


    # --------------------------------------------------------
    # Apply V5 temperature calibration
    # --------------------------------------------------------

    if TEMPERATURE > 0:

        probabilities = calibrate_probabilities(
            probabilities,
            TEMPERATURE
        )


    return probabilities


# ============================================================
# PREDICT
# ============================================================

def predict(image_bytes: bytes) -> dict:
    """
    Run V5 crop/disease classification.

    Parameters
    ----------
    image_bytes : bytes
        Raw image bytes.

    Returns
    -------
    dict

        {
            "crop": "...",
            "disease": "...",
            "confidence": 0.0,
            "status": "...",
            "top_3": [...]
        }
    """

    # ========================================================
    # LOAD IMAGE
    # ========================================================

    try:

        image = Image.open(
            io.BytesIO(image_bytes)
        )

    except Exception as e:

        raise ValueError(
            f"Unable to read image: {e}"
        )


    # ========================================================
    # PREPROCESS
    # ========================================================

    input_tensor = preprocess_image(
        image
    )


    # ========================================================
    # INPUT DIAGNOSTICS
    # ========================================================

    print(
        f"[V5 INPUT] "
        f"shape={input_tensor.shape} "
        f"dtype={input_tensor.dtype} "
        f"min={input_tensor.min():.2f} "
        f"max={input_tensor.max():.2f}"
    )


    # ========================================================
    # TFLITE INFERENCE
    # ========================================================

    interpreter.set_tensor(
        INPUT_INDEX,
        input_tensor
    )

    interpreter.invoke()


    # ========================================================
    # GET MODEL OUTPUT
    # ========================================================

    raw_output = interpreter.get_tensor(
        OUTPUT_INDEX
    )[0]


    # ========================================================
    # DE-QUANTIZE IF NECESSARY
    # ========================================================

    if OUTPUT_DTYPE in [
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


    # ========================================================
    # CONVERT OUTPUT TO PROBABILITIES
    # ========================================================

    probabilities = process_model_output(
        raw_output
    )


    # ========================================================
    # VERIFY PROBABILITIES
    # ========================================================

    probability_sum = np.sum(
        probabilities
    )

    if not np.isclose(
        probability_sum,
        1.0,
        atol=1e-4
    ):

        print(
            f"[WARN] Probability sum is "
            f"{probability_sum:.6f}"
        )


    # ========================================================
    # TOP-3 PREDICTIONS
    # ========================================================

    top_indices = np.argsort(
        probabilities
    )[::-1][:3]


    top_predictions = []


    for idx in top_indices:

        idx = int(idx)

        top_predictions.append({

            "disease": CLASS_NAMES[idx],

            "confidence": float(
                probabilities[idx]
            )

        })


    # ========================================================
    # BEST PREDICTION
    # ========================================================

    best_index = int(
        top_indices[0]
    )

    best_disease = CLASS_NAMES[
        best_index
    ]

    best_confidence = float(
        probabilities[best_index]
    )


    # ========================================================
    # DETERMINE CROP
    # ========================================================

    crop = best_disease.split(
        "_"
    )[0]


    # ========================================================
    # CONFIDENCE DECISION
    # ========================================================

    if (
        best_confidence
        >= CONFIDENCE_THRESHOLD
    ):

        status = "confident"

    else:

        status = "uncertain"


    # ========================================================
    # DIAGNOSTICS
    # ========================================================

    print(
        "--- V5 PREDICTION DIAGNOSTIC ---"
    )

    print(
        f"Top Class : {best_disease}"
    )

    print(
        f"Confidence: {best_confidence:.4f}"
    )

    print(
        f"Status    : {status}"
    )

    print(
        f"Temperature: {TEMPERATURE:.4f}"
    )

    print(
        f"Threshold : {CONFIDENCE_THRESHOLD:.4f}"
    )

    print(
        f"Top 3     : {top_predictions}"
    )

    print(
        "---------------------------------"
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================
    #
    # IMPORTANT:
    # This structure is intentionally kept identical
    # to your previous predictor.py.
    # ========================================================

    return {

        "crop": crop,

        "disease": best_disease,

        "confidence": best_confidence,

        "status": status,

        "top_3": top_predictions

    }