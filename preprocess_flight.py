import os
import glob
import sys
import numpy as np
import pandas as pd

BASE_DIR = os.path.expanduser("~/uav_project1")
OUTPUT_DIR = os.path.join(BASE_DIR, "processed_data")
TARGET_HZ = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

if len(sys.argv) != 2:
    print("Usage: python preprocess_flight.py <flight_number>")
    print("Example: python preprocess_flight.py 1")
    sys.exit(1)

flight_number = int(sys.argv[1])

DATA_DIR = os.path.join(
    BASE_DIR,
    f"data_flight{flight_number:02d}"
)

if not os.path.isdir(DATA_DIR):
    raise FileNotFoundError(
        f"Data directory not found: {DATA_DIR}"
    )

print("========================================")
print("       PX4 FLIGHT PREPROCESSING")
print("========================================")
print(f"Flight: {flight_number:02d}")
print(f"Input:  {DATA_DIR}")
print()

def find_csv(pattern):
    files = glob.glob(
        os.path.join(DATA_DIR, pattern)
    )

    if not files:
        raise FileNotFoundError(
            f"CSV not found: {pattern}"
        )

    return sorted(files)[0]


def clean(df):
    df = df.copy()

    df["timestamp"] = pd.to_numeric(
        df["timestamp"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["timestamp"]
    )

    df["time_sec"] = (
        df["timestamp"] - df["timestamp"].iloc[0]
    ) / 1_000_000.0

    df = df.drop_duplicates(
        "time_sec"
    )

    return df.sort_values(
        "time_sec"
    ).reset_index(drop=True)


def quaternion_to_euler(q0, q1, q2, q3):

    roll = np.arctan2(
        2 * (q0 * q1 + q2 * q3),
        1 - 2 * (q1 * q1 + q2 * q2)
    )

    sinp = 2 * (q0 * q2 - q3 * q1)
    sinp = np.clip(
        sinp,
        -1.0,
        1.0
    )

    pitch = np.arcsin(sinp)

    yaw = np.arctan2(
        2 * (q0 * q3 + q1 * q2),
        1 - 2 * (q2 * q2 + q3 * q3)
    )

    return roll, pitch, yaw


print("Loading local position...")

local = pd.read_csv(
    find_csv("*_vehicle_local_position_0.csv")
)

local = clean(local)

local = local[
    [
        "time_sec",
        "x", "y", "z",
        "vx", "vy", "vz",
        "ax", "ay", "az"
    ]
]

print(f"Local samples: {len(local)}")


print("Loading attitude...")

attitude = pd.read_csv(
    find_csv("*_vehicle_attitude_0.csv")
)

attitude = clean(attitude)

roll, pitch, yaw = quaternion_to_euler(
    attitude["q[0]"].values,
    attitude["q[1]"].values,
    attitude["q[2]"].values,
    attitude["q[3]"].values
)

attitude["roll"] = roll
attitude["pitch"] = pitch
attitude["yaw"] = yaw

attitude = attitude[
    [
        "time_sec",
        "roll",
        "pitch",
        "yaw"
    ]
]

print(f"Attitude samples: {len(attitude)}")


print("Loading angular velocity...")

angular = pd.read_csv(
    find_csv("*_vehicle_angular_velocity_0.csv")
)

angular = clean(angular)

angular = angular[
    [
        "time_sec",
        "xyz[0]",
        "xyz[1]",
        "xyz[2]"
    ]
]

angular = angular.rename(
    columns={
        "xyz[0]": "angular_x",
        "xyz[1]": "angular_y",
        "xyz[2]": "angular_z"
    }
)

print(f"Angular samples: {len(angular)}")


print("Loading battery...")

battery = pd.read_csv(
    find_csv("*_battery_status_0.csv")
)

battery = clean(battery)

battery = battery[
    [
        "time_sec",
        "voltage_v",
        "current_a",
        "remaining"
    ]
]

print(f"Battery samples: {len(battery)}")


print("Loading motors...")

motor = pd.read_csv(
    find_csv("*_actuator_motors_0.csv")
)

motor = clean(motor)

motor = motor[
    [
        "time_sec",
        "control[0]",
        "control[1]",
        "control[2]",
        "control[3]"
    ]
]

motor = motor.rename(
    columns={
        "control[0]": "motor_1",
        "control[1]": "motor_2",
        "control[2]": "motor_3",
        "control[3]": "motor_4"
    }
)

print(f"Motor samples: {len(motor)}")


print()
print(f"Creating {TARGET_HZ} Hz timeline...")

start = max(
    local["time_sec"].min(),
    attitude["time_sec"].min(),
    angular["time_sec"].min(),
    battery["time_sec"].min(),
    motor["time_sec"].min()
)

end = min(
    local["time_sec"].max(),
    attitude["time_sec"].max(),
    angular["time_sec"].max(),
    battery["time_sec"].max(),
    motor["time_sec"].max()
)

timeline = np.arange(
    start,
    end + 0.01,
    1.0 / TARGET_HZ
)

merged = pd.DataFrame(
    {"time_sec": timeline}
)


def merge_stream(base, stream):

    return pd.merge_asof(
        base.sort_values("time_sec"),
        stream.sort_values("time_sec"),
        on="time_sec",
        direction="nearest",
        tolerance=0.15
    )


print("Synchronizing telemetry...")

merged = merge_stream(
    merged,
    local
)

merged = merge_stream(
    merged,
    attitude
)

merged = merge_stream(
    merged,
    angular
)

merged = merge_stream(
    merged,
    battery
)

merged = merge_stream(
    merged,
    motor
)


features = [
    "x", "y", "z",
    "vx", "vy", "vz",
    "ax", "ay", "az",
    "roll", "pitch", "yaw",
    "angular_x", "angular_y", "angular_z",
    "voltage_v",
    "current_a",
    "remaining",
    "motor_1", "motor_2", "motor_3", "motor_4"
]


print("Cleaning NaN and infinite values...")

merged[features] = merged[
    features
].replace(
    [np.inf, -np.inf],
    np.nan
)

merged[features] = merged[
    features
].interpolate()

merged[features] = merged[
    features
].ffill()

merged[features] = merged[
    features
].bfill()

merged = merged.dropna(
    subset=features
)

merged = merged.reset_index(
    drop=True
)


print()
print("Checking constant features...")

for feature in features:

    if merged[feature].nunique() <= 1:

        print(
            f"Constant feature: {feature}"
        )


output_file = os.path.join(
    OUTPUT_DIR,
    f"flight{flight_number:02d}_processed.csv"
)

merged.to_csv(
    output_file,
    index=False
)


duration = (
    merged["time_sec"].iloc[-1]
    - merged["time_sec"].iloc[0]
)


print()
print("========================================")
print("    PREPROCESSING COMPLETED")
print("========================================")
print(f"Flight       : {flight_number:02d}")
print(f"Samples      : {len(merged)}")
print(f"Features     : {len(features)}")
print(f"Sampling     : {TARGET_HZ} Hz")
print(f"Duration     : {duration:.2f} seconds")
print(f"Output       : {output_file}")
print("========================================")
