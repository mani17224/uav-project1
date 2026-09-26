import os
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.expanduser("~/uav_project1")
DATA_DIR = os.path.join(BASE_DIR, "window_data")

MODEL_FILE = os.path.join(DATA_DIR, "uav_autoencoder.keras")
VAL_FILE = os.path.join(DATA_DIR, "X_val.npy")
THRESHOLD_FILE = os.path.join(DATA_DIR, "anomaly_threshold.npy")

print("========================================")
print("       NORMAL DATA EVALUATION")
print("========================================")

model = tf.keras.models.load_model(MODEL_FILE)
X_val = np.load(VAL_FILE)
threshold = float(np.load(THRESHOLD_FILE))

X_reconstructed = model.predict(X_val, verbose=0)

errors = np.mean(
    np.square(X_val - X_reconstructed),
    axis=(1, 2)
)

predictions = errors > threshold

normal_count = np.sum(~predictions)
anomaly_count = np.sum(predictions)

false_positive_rate = (
    anomaly_count / len(X_val)
) * 100

print()
print(f"Validation windows : {len(X_val)}")
print(f"Threshold          : {threshold:.6f}")
print()
print(f"Predicted NORMAL   : {normal_count}")
print(f"Predicted ANOMALY  : {anomaly_count}")
print(f"False Positive Rate: {false_positive_rate:.2f}%")

print()
print("========================================")
print("       EVALUATION COMPLETED")
print("========================================")
