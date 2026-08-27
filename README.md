# plant-disease-detector

Model

The project uses a MobileNetV3-Large image classification model optimized for plant disease detection. The trained model is converted to TensorFlow Lite (TFLite) for efficient inference. It supports 27 crop/disease classes and uses confidence calibration to distinguish between confident and uncertain predictions.

Dataset

The dataset is a combined multi-crop plant disease dataset containing images of `cotton`, `groundnut`, `ragi`, `rice`, and `sugarcane'. It includes both healthy and diseased plant images, covering the 27 classes supported by the classifier. The dataset was organized into class-specific folders and preprocessed before training.
