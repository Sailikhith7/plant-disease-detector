import json
import io
import os
import numpy as np
from PIL import Image, ImageStat

# ============================================================
# PATHS & CONFIG
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "weights", "crop_classifier_v1.tflite")
LABELS_PATH = os.path.join(BASE_DIR, "labels.json")
CALIBRATION_PATH = os.path.join(BASE_DIR, "calibration.json")

# ============================================================
# LOAD LABELS & CALIBRATION
# ============================================================

with open(LABELS_PATH, "r") as f:
    labels_data = json.load(f)

if isinstance(labels_data, dict):
    CLASS_NAMES = [labels_data[str(i)] for i in range(len(labels_data))]
else:
    CLASS_NAMES = labels_data

TEMPERATURE = 1.0
CONFIDENCE_THRESHOLD = 0.70

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
# IMAGE SANITY & LEAF DETECTION FILTER
# ============================================================

def is_valid_leaf_image(image: Image.Image) -> tuple[bool, str]:
    """
    Validates that the input image contains actual plant foliage and
    rejects human faces, skin, blank walls, or random objects.
    """
    img_rgb = image.convert("RGB")
    stat = ImageStat.Stat(img_rgb.convert("L"))
    mean_brightness = stat.mean[0]
    std_dev = stat.stddev[0]

    # 1. Dark/Overexposed Filter
    if mean_brightness < 25.0 or std_dev < 12.0:
        return False, "Image is too dark or empty. Please ensure proper lighting."
    if mean_brightness > 240.0 and std_dev < 12.0:
        return False, "Image is overexposed. Please adjust lighting."

    # Convert to NumPy array
    arr = np.array(img_rgb, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # 2. Vegetation Color Check: Excess Green Index (2G - R - B) & Chlorotic Yellows
    # Healthy & diseased crop foliage will have positive greenness or specific yellow/brown leaf hues
    excess_green = (2.0 * g) - r - b
    green_pixels = (excess_green > 10.0) | ((g > 60) & (r > 60) & (g > b + 15))  # Green and yellowed diseased foliage
    green_ratio = np.count_nonzero(green_pixels) / (arr.shape[0] * arr.shape[1])

    # 3. Human Skin Tone Check
    # Typical normalized skin condition in RGB space: R > G > B, with specific bounds
    skin_pixels = (r > 95) & (g > 40) & (b > 20) & ((r - g) > 15) & (r > b) & ((np.maximum(r, np.maximum(g, b)) - np.minimum(r, np.minimum(g, b))) > 15)
    skin_ratio = np.count_nonzero(skin_pixels) / (arr.shape[0] * arr.shape[1])

    # If skin dominates the photo, reject as human/selfie
    if skin_ratio > 0.25 and green_ratio < 0.10:
        return False, "No leaf detected. Please focus the camera on an infected crop leaf."

    # If there is virtually no foliage in the frame, reject random objects
    if green_ratio < 0.08:
        return False, "No plant foliage detected. Please center an infected leaf in the frame."

    return True, "Valid"

# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB")
    
    if INPUT_SHAPE[1] == 3:  # NCHW
        target_h, target_w = int(INPUT_SHAPE[2]), int(INPUT_SHAPE[3])
    else:  # NHWC
        target_h, target_w = int(INPUT_SHAPE[1]), int(INPUT_SHAPE[2])

    # Center-crop to square before resizing to prevent distortion
    w, h = image.size
    min_dim = min(w, h)
    left = (w - min_dim) / 2
    top = (h - min_dim) / 2
    right = (w + min_dim) / 2
    bottom = (h + min_dim) / 2
    image = image.crop((left, top, right, bottom))
    image = image.resize((target_w, target_h), Image.Resampling.BILINEAR)

    img_array = np.asarray(image, dtype=np.float32) / 255.0

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

    # 1. Pre-Inference Sanity Validation (from Step 1)
    is_valid, reason = is_valid_leaf_image(image)
    if not is_valid:
        return {
            "crop": "Unknown",
            "disease": "No Plant Detected",
            "confidence": 0.0,
            "status": "invalid_input",
            "response": reason,
            "top_3": []
        }

    # 2. Run Neural Network Inference
    input_tensor = preprocess_image(image)
    interpreter.set_tensor(INPUT_INDEX, input_tensor)
    interpreter.invoke()

    # Get raw logits directly from the output tensor
    raw_output = interpreter.get_tensor(OUTPUT_INDEX)[0]

    # De-quantize if output is uint8/int8
    if OUTPUT_DETAILS[0]["dtype"] in [np.uint8, np.int8]:
        scale, zero_point = OUTPUT_DETAILS[0]["quantization"]
        if scale > 0:
            raw_output = scale * (raw_output.astype(np.float32) - zero_point)

    # -------------------------------------------------------------
    # STEP 2: OPEN-SET MAXIMUM LOGIT THRESHOLDING
    # -------------------------------------------------------------
    max_logit = float(np.max(raw_output))
    
    # Calculate calibrated probabilities for diagnostic logging
    calibrated_logits = raw_output / TEMPERATURE
    probabilities = softmax(calibrated_logits)

    top_indices = np.argsort(probabilities)[::-1][:3]
    top_predictions = [
        {"disease": CLASS_NAMES[idx], "confidence": float(probabilities[idx])}
        for idx in top_indices
    ]

    best_index = int(top_indices[0])
    best_disease = CLASS_NAMES[best_index]
    best_confidence = float(probabilities[best_index])
    
    # If the maximum logit is below 3.5, the model does not recognize any clear disease pattern
    if max_logit < 3.5:
        print(f"[OOD DETECTED] Max Logit is {max_logit:.3f} (< 3.5). Rejecting as non-crop/unrecognized.")
        return {
            "crop": "Unknown",
            "disease": "Unrecognized Sample",
            "confidence": best_confidence,
            "status": "uncertain",
            "response": "The model could not detect clear crop disease symptoms. Please center a well-lit infected leaf in the frame and retake the photo.",
            "top_3": top_predictions
        }

    # If logit is strong, process normally
    crop = best_disease.split("_")[0]
    status = "confident" if best_confidence >= CONFIDENCE_THRESHOLD else "uncertain"

    print("--- PREDICTION DIAGNOSTIC ---")
    print(f"Top Class: {best_disease} | Conf: {best_confidence*100:.2f}% | Max Logit: {max_logit:.3f} | Status: {status}")
    print("-----------------------------")

    return {
        "crop": crop,
        "disease": best_disease,
        "confidence": best_confidence,
        "status": status,
        "top_3": top_predictions
    }