import pandas as pd

NORMAL_FILE = "processed_data/normal_flights.csv"
ABNORMAL_FILE = "processed_data/abnormal_flight_processed.csv"
OUTPUT_FILE = "processed_data/uav_labeled_dataset.csv"

features = [
    "time_sec",
    "x", "y", "z",
    "vx", "vy", "vz",
    "ax", "ay", "az",
    "roll", "pitch", "yaw",
    "angular_x", "angular_y", "angular_z",
    "voltage_v", "remaining",
    "motor_1", "motor_2", "motor_3", "motor_4"
]

normal = pd.read_csv(NORMAL_FILE)
abnormal = pd.read_csv(ABNORMAL_FILE)

normal["label"] = 0
abnormal["flight_id"] = 3

normal = normal[features + ["flight_id", "label"]]
abnormal = abnormal[features + ["flight_id", "label"]]

combined = pd.concat(
    [normal, abnormal],
    ignore_index=True
)

combined.to_csv(
    OUTPUT_FILE,
    index=False
)

print("========================================")
print("      UAV LABELED DATASET CREATED")
print("========================================")
print(f"Normal samples   : {(combined['label'] == 0).sum()}")
print(f"Abnormal samples : {(combined['label'] == 1).sum()}")
print(f"Total samples    : {len(combined)}")
print(f"Total columns    : {len(combined.columns)}")
print(f"Output file      : {OUTPUT_FILE}")
print()
print("Samples per flight:")
print(combined.groupby(["flight_id", "label"]).size())
print()
print("Saved successfully!")
print("========================================")
