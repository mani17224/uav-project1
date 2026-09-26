import os
import numpy as np
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.expanduser("~/uav_project1")

INPUT_FILE = os.path.join(
    BASE_DIR,
    "window_data",
    "normal_windows_scaled.npy"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "window_data"
)

print("========================================")
print("       SPLITTING NORMAL DATA")
print("========================================")

X = np.load(INPUT_FILE)

print(f"Total windows: {len(X)}")

X_train, X_val = train_test_split(
    X,
    test_size=0.20,
    random_state=42,
    shuffle=True
)

train_file = os.path.join(
    OUTPUT_DIR,
    "X_train.npy"
)

val_file = os.path.join(
    OUTPUT_DIR,
    "X_val.npy"
)

np.save(train_file, X_train)
np.save(val_file, X_val)

print()
print("========================================")
print("       SPLIT COMPLETED")
print("========================================")

print(f"Training windows   : {len(X_train)}")
print(f"Validation windows : {len(X_val)}")

print(f"Training shape     : {X_train.shape}")
print(f"Validation shape   : {X_val.shape}")

print()
print(f"Training data saved   : {train_file}")
print(f"Validation data saved : {val_file}")

print("========================================")
