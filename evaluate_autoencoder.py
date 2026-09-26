import numpy as np
import pandas as pd
from tensorflow import keras
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

DATA_FILE = "processed_data/uav_windows_ml.npz"
MODEL_FILE = "processed_data/uav_autoencoder.keras"

RESULT_FILE = "processed_data/autoencoder_results.csv"
THRESHOLD_FILE = "processed_data/anomaly_threshold.txt"

print("========================================")
print("     AUTOENCODER BASELINE EVALUATION")
print("========================================")

# Load data
data = np.load(DATA_FILE)

X = data["X"]
y = data["y"]
flight_ids = data["flight_ids"]

print(f"Total windows : {len(X)}")
print(f"Normal       : {(y == 0).sum()}")
print(f"Abnormal     : {(y == 1).sum()}")

# Load trained model
model = keras.models.load_model(MODEL_FILE)

print()
print("Calculating reconstruction errors...")

# Reconstruction
X_reconstructed = model.predict(X, verbose=0)

# MSE for each window
errors = np.mean(
    np.square(X - X_reconstructed),
    axis=(1, 2)
)

# Calculate threshold ONLY from normal windows
normal_errors = errors[y == 0]

normal_mean = normal_errors.mean()
normal_std = normal_errors.std()

threshold = normal_mean + 3 * normal_std

print()
print("Threshold calculation:")
print(f"Normal mean : {normal_mean:.6f}")
print(f"Normal std  : {normal_std:.6f}")
print(f"Threshold   : {threshold:.6f}")

# Predictions
predictions = (errors > threshold).astype(int)

# Metrics
accuracy = accuracy_score(y, predictions)
precision = precision_score(
    y, predictions, zero_division=0
)
recall = recall_score(
    y, predictions, zero_division=0
)
f1 = f1_score(
    y, predictions, zero_division=0
)

# Confusion matrix
tn, fp, fn, tp = confusion_matrix(
    y, predictions
).ravel()

print()
print("========================================")
print("             RESULTS")
print("========================================")

print(f"Accuracy  : {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"Precision : {precision:.4f} ({precision * 100:.2f}%)")
print(f"Recall    : {recall:.4f} ({recall * 100:.2f}%)")
print(f"F1 Score  : {f1:.4f} ({f1 * 100:.2f}%)")

print()
print("Confusion Matrix:")
print(f"TN = {tn}")
print(f"FP = {fp}")
print(f"FN = {fn}")
print(f"TP = {tp}")

# Save threshold
with open(THRESHOLD_FILE, "w") as f:
    f.write(str(threshold))

# Save detailed results
results = pd.DataFrame({
    "window_index": np.arange(len(X)),
    "flight_id": flight_ids,
    "actual_label": y,
    "reconstruction_error": errors,
    "predicted_label": predictions
})

results.to_csv(
    RESULT_FILE,
    index=False
)

print()
print("Files saved:")
print(f"Results   : {RESULT_FILE}")
print(f"Threshold : {THRESHOLD_FILE}")

print()
print("Evaluation completed.")
print("========================================")
