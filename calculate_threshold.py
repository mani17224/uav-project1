import os
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.expanduser("~/uav_project1")
DATA_DIR = os.path.join(BASE_DIR, "window_data")

MODEL_FILE = os.path.join(
    DATA_DIR,
    "uav_autoencoder.keras"
)

VAL_FILE = os.path.join(
    DATA_DIR,
    "X_val.npy"
)

THRESHOLD_FILE = os.path.join(
    DATA_DIR,
    "anomaly_threshold.npy"
)

print("========================================")
print("   CALCULATING ANOMALY THRESHOLD")
print("========================================")

print("Loading model...")

model = tf.keras.models.load_model(
    MODEL_FILE
)

print("Loading validation data...")

X_val = np.load(VAL_FILE)

print(f"Validation shape: {X_val.shape}")

print()
print("Reconstructing validation windows...")

X_reconstructed = model.predict(
    X_val,
    verbose=1
)

# Calculate MSE for every window
reconstruction_errors = np.mean(
    np.square(X_val - X_reconstructed),
    axis=(1, 2)
)

print()
print("Reconstruction error statistics:")

print(
    f"Minimum : {reconstruction_errors.min():.6f}"
)

print(
    f"Maximum : {reconstruction_errors.max():.6f}"
)

print(
    f"Mean    : {reconstruction_errors.mean():.6f}"
)

print(
    f"Median  : {np.median(reconstruction_errors):.6f}"
)

print(
    f"Std     : {reconstruction_errors.std():.6f}"
)

# Initial baseline threshold:
# mean + 3 standard deviations
threshold = (
    reconstruction_errors.mean()
    + 3 * reconstruction_errors.std()
)

np.save(
    THRESHOLD_FILE,
    threshold
)

print()
print("========================================")
print("       THRESHOLD CREATED")
print("========================================")

print(
    f"Anomaly threshold : {threshold:.6f}"
)

print(
    f"Saved to          : {THRESHOLD_FILE}"
)

print()
print("Interpretation:")
print("Error <= threshold → NORMAL")
print("Error > threshold  → ANOMALY")

print("========================================")
