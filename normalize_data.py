import os
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib

BASE_DIR = os.path.expanduser("~/uav_project1")

INPUT_FILE = os.path.join(
    BASE_DIR,
    "window_data",
    "normal_windows.npy"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "window_data",
    "normal_windows_scaled.npy"
)

SCALER_FILE = os.path.join(
    BASE_DIR,
    "window_data",
    "scaler.pkl"
)

print("========================================")
print("       NORMALIZING UAV DATA")
print("========================================")

windows = np.load(INPUT_FILE)

print(f"Original shape: {windows.shape}")

num_windows, window_size, num_features = windows.shape

# Reshape so StandardScaler can work feature-wise
data_2d = windows.reshape(
    -1,
    num_features
)

print(f"Data for scaling: {data_2d.shape}")

scaler = StandardScaler()

scaled_2d = scaler.fit_transform(data_2d)

scaled_windows = scaled_2d.reshape(
    num_windows,
    window_size,
    num_features
).astype(np.float32)

np.save(
    OUTPUT_FILE,
    scaled_windows
)

joblib.dump(
    scaler,
    SCALER_FILE
)

print()
print("========================================")
print("       NORMALIZATION COMPLETED")
print("========================================")

print(f"Scaled shape : {scaled_windows.shape}")
print(f"Saved data   : {OUTPUT_FILE}")
print(f"Saved scaler : {SCALER_FILE}")

print()
print("Checking statistics...")

print(
    f"Mean: {scaled_2d.mean():.6f}"
)

print(
    f"Std : {scaled_2d.std():.6f}"
)

print("========================================")
