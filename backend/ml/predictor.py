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

TEMPERATURE = 1.0
CONFIDENCE_THRESHOLD = 0.75

if os.path.exists(CALIBRATION_PATH):
    try:
        with open(CALIBRATION_PATH, "r") as f:
            calibration = json.load(f)
        TEMPERATURE = float(calibration.get("temperature", 1.0))
        CONFIDENCE_THRESHOLD = float(calibration.get("confidence_threshold", 0.70))
    except Exception as e:
        print(f"[WARN] Failed to read calibration.json: {e}")

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

interpreter = Interpreter(model_path=MODEL_PATH)
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
    
    # Determine height/width from model input shape
    if INPUT_SHAPE[1] == 3:  # NCHW
        target_h, target_w = int(INPUT_SHAPE[2]), int(INPUT_SHAPE[3])
    else:  # NHWC (Standard [1, 224, 224, 3])
        target_h, target_w = int(INPUT_SHAPE[1]), int(INPUT_SHAPE[2])

    image = image.resize((target_w, target_h))
    img_array = np.asarray(image, dtype=np.float32)

    # Normalize based on data type
    if INPUT_DTYPE == np.uint8:
        img_array = img_array.astype(np.uint8)
    else:
        # Standard [0, 1] normalization for MobileNet/TFLite models
        img_array = img_array / 255.0

    # Adjust channel ordering if NCHW
    if INPUT_SHAPE[1] == 3 and len(img_array.shape) == 3:
        img_array = np.transpose(img_array, (2, 0, 1))

    img_tensor = np.expand_dims(img_array, axis=0)
    return img_tensor.astype(INPUT_DTYPE)

# ============================================================
# SOFTMAX
# ============================================================

def softmax(logits):
    logits = np.array(logits, dtype=np.float64)
    logits = logits - np.max(logits)
    exp_values = np.exp(logits)
    return (exp_values / np.sum(exp_values)).astype(np.float32)

# ============================================================
# PREDICT
# ============================================================

def predict(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes))
    input_tensor = preprocess_image(image)

    interpreter.set_tensor(INPUT_INDEX, input_tensor)
    interpreter.invoke()

    raw_output = interpreter.get_tensor(OUTPUT_INDEX)[0]

    # De-quantize if output is uint8/int8
    if OUTPUT_DETAILS[0]["dtype"] in [np.uint8, np.int8]:
        scale, zero_point = OUTPUT_DETAILS[0]["quantization"]
        if scale > 0:
            raw_output = scale * (raw_output.astype(np.float32) - zero_point)

    # Temperature scaling
    calibrated_logits = raw_output / TEMPERATURE
    probabilities = softmax(calibrated_logits)

    top_indices = np.argsort(probabilities)[::-1][:3]
    
    top_predictions = []
    for idx in top_indices:
        top_predictions.append({
            "disease": CLASS_NAMES[idx],
            "confidence": float(probabilities[idx])
        })

    best_index = int(top_indices[0])
    best_disease = CLASS_NAMES[best_index]
    best_confidence = float(probabilities[best_index])
    
    # Extract crop prefix
    crop = best_disease.split("_")[0]

    status = "confident" if best_confidence >= CONFIDENCE_THRESHOLD else "uncertain"

    print("--- PREDICTION DIAGNOSTIC ---")
    print(f"Top Class: {best_disease} | Conf: {best_confidence:.4f} | Status: {status}")
    print(f"Top 3: {top_predictions}")
    print("-----------------------------")

    return {
        "crop": crop,
        "disease": best_disease,
        "confidence": best_confidence,
        "status": status,
        "top_3": top_predictions
    }