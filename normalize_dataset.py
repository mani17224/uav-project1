import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

INPUT_FILE = "processed_data/uav_labeled_dataset.csv"
OUTPUT_FILE = "processed_data/uav_normalized.csv"
SCALER_FILE = "processed_data/standard_scaler.pkl"

FEATURES = [
    "x", "y", "z",
    "vx", "vy", "vz",
    "ax", "ay", "az",
    "roll", "pitch", "yaw",
    "angular_x", "angular_y", "angular_z",
    "voltage_v", "remaining",
    "motor_1", "motor_2", "motor_3", "motor_4",
    "time_sec"
]

print("========================================")
print("       UAV DATA NORMALIZATION")
print("========================================")

df = pd.read_csv(INPUT_FILE)

normal = df[df["label"] == 0].copy()

print(f"Total samples      : {len(df)}")
print(f"Normal samples     : {len(normal)}")
print(f"Abnormal samples   : {(df['label'] == 1).sum()}")
print(f"Features           : {len(FEATURES)}")

# Fit scaler ONLY on normal data
scaler = StandardScaler()

scaler.fit(normal[FEATURES])

# Transform complete dataset using normal-trained scaler
df[FEATURES] = scaler.transform(df[FEATURES])

# Save normalized dataset
df.to_csv(
    OUTPUT_FILE,
    index=False
)

# Save scaler for future inference
joblib.dump(
    scaler,
    SCALER_FILE
)

print()
print("Normalization completed.")
print(f"Normalized dataset : {OUTPUT_FILE}")
print(f"Scaler              : {SCALER_FILE}")

print()
print("Normal-data statistics after scaling:")

check = df[df["label"] == 0]

print(
    check[FEATURES].mean().round(4).head(10)
)

print()
print("Saved successfully!")
print("========================================")
