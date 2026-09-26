import os
import numpy as np
import pandas as pd

INPUT_FILE = "processed_data/uav_normalized.csv"
OUTPUT_FILE = "processed_data/uav_windows.npz"

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

WINDOW_SIZE = 20
STEP = 5

print("========================================")
print("        UAV TIME-WINDOW CREATION")
print("========================================")

df = pd.read_csv(INPUT_FILE)

windows = []
labels = []
flight_ids = []

# Create windows separately for each flight
# so a window never crosses from one flight into another.
for flight_id, flight_df in df.groupby("flight_id"):

    flight_df = flight_df.sort_values("time_sec").reset_index(drop=True)

    values = flight_df[FEATURES].values
    flight_labels = flight_df["label"].values

    for start in range(
        0,
        len(values) - WINDOW_SIZE + 1,
        STEP
    ):

        end = start + WINDOW_SIZE

        window = values[start:end]

        # Window is abnormal if any sample inside it is abnormal.
        window_label = int(
            flight_labels[start:end].max()
        )

        windows.append(window)
        labels.append(window_label)
        flight_ids.append(flight_id)


X = np.array(windows, dtype=np.float32)
y = np.array(labels, dtype=np.int64)
ids = np.array(flight_ids, dtype=np.int64)


np.savez_compressed(
    OUTPUT_FILE,
    X=X,
    y=y,
    flight_ids=ids
)


print()
print("Window generation completed.")
print(f"Window size       : {WINDOW_SIZE} samples")
print(f"Step size         : {STEP} samples")
print(f"Feature count     : {len(FEATURES)}")
print(f"Window shape      : {X.shape}")
print(f"Normal windows    : {(y == 0).sum()}")
print(f"Abnormal windows  : {(y == 1).sum()}")
print(f"Output file       : {OUTPUT_FILE}")

print()
print("Saved successfully!")
print("========================================")
