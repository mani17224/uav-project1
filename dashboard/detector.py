from pathlib import Path
import sys

import joblib
import numpy as np
from tensorflow import keras

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from transformer_model import PositionalEmbedding


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed_data"

MODEL_PATH = PROCESSED_DIR / "uav_transformer_encoder.keras"
SCALER_PATH = PROCESSED_DIR / "standard_scaler.pkl"
MEAN_PATH = PROCESSED_DIR / "mahalanobis_mean.npy"
INV_COV_PATH = PROCESSED_DIR / "mahalanobis_inv_cov.npy"
THRESHOLD_PATH = PROCESSED_DIR / "transformer_mahalanobis_threshold.txt"


print("Loading Transformer model...")
model = keras.models.load_model(
    MODEL_PATH,
    custom_objects={"PositionalEmbedding": PositionalEmbedding}
)

print("Loading StandardScaler...")
scaler = joblib.load(SCALER_PATH)

print("Loading Mahalanobis mean...")
mahalanobis_mean = np.load(MEAN_PATH)

print("Loading inverse covariance...")
mahalanobis_inv_cov = np.load(INV_COV_PATH)

print("Loading Mahalanobis threshold...")
threshold = float(THRESHOLD_PATH.read_text().strip())

print()
print("========================================")
print("       UAV AI DETECTOR READY")
print("========================================")
print(f"Transformer input : (20, 21)")
print(f"Transformer output: (128,)")
print(f"Mahalanobis threshold: {threshold:.6f}")
print("Model loaded successfully.")
print("========================================")


def get_embedding(window):
    """
    Convert one UAV telemetry window of shape (20, 21)
    into a 128-dimensional Transformer embedding.
    """

    window = np.asarray(window, dtype=np.float32)

    if window.shape != (20, 21):
        raise ValueError(
            f"Expected window shape (20, 21), got {window.shape}"
        )

    batch = np.expand_dims(window, axis=0)

    embedding = model.predict(batch, verbose=0)[0]

    return embedding.astype(np.float64)


def mahalanobis_distance(embedding):
    """
    Calculate Mahalanobis distance from the normal embedding distribution.
    """

    diff = embedding - mahalanobis_mean

    distance_squared = np.einsum(
        "i,ij,j->",
        diff,
        mahalanobis_inv_cov,
        diff
    )

    distance_squared = max(float(distance_squared), 0.0)

    return float(np.sqrt(distance_squared))


def detect(window):
    """
    Run complete UAV anomaly detection.

    Returns:
        score
        threshold
        status
    """

    embedding = get_embedding(window)

    score = mahalanobis_distance(embedding)

    status = "ANOMALY" if score > threshold else "NORMAL"

    return {
        "score": score,
        "threshold": threshold,
        "status": status
    }
