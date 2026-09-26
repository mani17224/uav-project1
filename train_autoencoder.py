import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

INPUT_FILE = "processed_data/uav_windows_ml.npz"
MODEL_FILE = "processed_data/uav_autoencoder.keras"

print("========================================")
print("       UAV AUTOENCODER TRAINING")
print("========================================")

# Load dataset
data = np.load(INPUT_FILE)

X = data["X"]
y = data["y"]
flight_ids = data["flight_ids"]

# Use ONLY normal windows for training
X_normal = X[y == 0]

print(f"Total windows      : {len(X)}")
print(f"Normal windows     : {len(X_normal)}")
print(f"Abnormal windows   : {(y == 1).sum()}")
print(f"Input shape        : {X_normal.shape}")

# Build Autoencoder
model = keras.Sequential([
    layers.Input(shape=(20, 21)),

    layers.Flatten(),

    layers.Dense(128, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(32, activation="relu"),

    layers.Dense(64, activation="relu"),
    layers.Dense(128, activation="relu"),

    layers.Dense(20 * 21),
    layers.Reshape((20, 21))
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="mse"
)

print()
print("Model architecture:")
model.summary()

print()
print("Starting training...")

history = model.fit(
    X_normal,
    X_normal,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    shuffle=True,
    verbose=1
)

# Save model
model.save(MODEL_FILE)

print()
print("Training completed!")
print(f"Model saved       : {MODEL_FILE}")

print()
print("Final training loss   :", history.history["loss"][-1])
print("Final validation loss :", history.history["val_loss"][-1])

print("========================================")
