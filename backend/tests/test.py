from backend.ml.predictor import predict


IMAGE_PATH = r"C:\Plant Detector\test_images\download.jpg"


with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()


result = predict(image_bytes)

print("\nPrediction:")
print(result)