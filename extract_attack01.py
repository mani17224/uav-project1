from pyulog import ULog
import pandas as pd
import numpy as np
import os

ulog_path = "data_attack01/17_45_34.ulg"
output_path = "data_attack01/attack01_raw.csv"

print("Loading ULog...")
ulog = ULog(ulog_path)

datasets = {d.name: d.data for d in ulog.data_list}

print("Available datasets:", len(datasets))

# Required datasets
required = [
    "vehicle_local_position",
    "vehicle_attitude",
    "vehicle_angular_velocity",
    "battery_status",
    "actuator_motors",
    "vehicle_gps_position",
]

for name in required:
    if name in datasets:
        print(f"{name}: available")
    else:
        print(f"{name}: NOT FOUND")

# Extract main datasets
local = datasets["vehicle_local_position"]
attitude = datasets["vehicle_attitude"]
angular = datasets["vehicle_angular_velocity"]
battery = datasets["battery_status"]
motors = datasets["actuator_motors"]
gps = datasets["vehicle_gps_position"]

print("\nExtracting telemetry...")

# Local position
df_local = pd.DataFrame({
    "timestamp": local["timestamp"],
    "x": local["x"],
    "y": local["y"],
    "z": local["z"],
    "vx": local["vx"],
    "vy": local["vy"],
    "vz": local["vz"],
    "ax": local["ax"],
    "ay": local["ay"],
    "az": local["az"],
})

# Attitude
df_att = pd.DataFrame({
    "timestamp": attitude["timestamp"],
    "q0": attitude["q[0]"],
    "q1": attitude["q[1]"],
    "q2": attitude["q[2]"],
    "q3": attitude["q[3]"],
})

# Angular velocity
df_ang = pd.DataFrame({
    "timestamp": angular["timestamp"],
    "angular_x": angular["xyz[0]"],
    "angular_y": angular["xyz[1]"],
    "angular_z": angular["xyz[2]"],
})

# Battery
df_bat = pd.DataFrame({
    "timestamp": battery["timestamp"],
    "voltage_v": battery["voltage_v"],
    "current_a": battery["current_a"],
    "remaining": battery["remaining"],
})

# Motors
df_motor = pd.DataFrame({
    "timestamp": motors["timestamp"],
    "motor_1": motors["control[0]"],
    "motor_2": motors["control[1]"],
    "motor_3": motors["control[2]"],
    "motor_4": motors["control[3]"],
})

# GPS
df_gps = pd.DataFrame({
    "timestamp": gps["timestamp"],
    "latitude_deg": gps["latitude_deg"],
    "longitude_deg": gps["longitude_deg"],
    "gps_vel_m_s": gps["vel_m_s"],
    "fix_type": gps["fix_type"],
    "satellites_used": gps["satellites_used"],
    "spoofing_state": gps["spoofing_state"],
    "jamming_state": gps["jamming_state"],
})

# Convert timestamps to seconds
for df in [
    df_local,
    df_att,
    df_ang,
    df_bat,
    df_motor,
    df_gps,
]:
    df["time_sec"] = df["timestamp"] / 1_000_000.0

# Use local position as the main 10 Hz timeline
base = df_local.drop(columns=["timestamp"]).sort_values("time_sec").copy()

base = pd.merge_asof(
    base,
    df_att.drop(columns=["timestamp"]).sort_values("time_sec"),
    on="time_sec",
    direction="nearest",
    tolerance=0.15,
)

base = pd.merge_asof(
    base,
    df_ang.drop(columns=["timestamp"]).sort_values("time_sec"),
    on="time_sec",
    direction="nearest",
    tolerance=0.15,
)

base = pd.merge_asof(
    base,
    df_bat.drop(columns=["timestamp"]).sort_values("time_sec"),
    on="time_sec",
    direction="nearest",
    tolerance=0.15,
)

base = pd.merge_asof(
    base,
    df_motor.drop(columns=["timestamp"]).sort_values("time_sec"),
    on="time_sec",
    direction="nearest",
    tolerance=0.15,
)

base = pd.merge_asof(
    base,
    df_gps.drop(columns=["timestamp"]).sort_values("time_sec"),
    on="time_sec",
    direction="nearest",
    tolerance=0.15,
)

# Remove duplicate timestamp columns
if "timestamp" in base.columns:
    base = base.drop(columns=["timestamp"])

# Fill missing values
base = base.interpolate()
base = base.ffill()
base = base.bfill()

# Normalize time to start at zero
base["time_sec"] = base["time_sec"] - base["time_sec"].iloc[0]

# Convert quaternion to Euler angles
def quaternion_to_euler(q0, q1, q2, q3):

    roll = np.arctan2(
        2 * (q0 * q1 + q2 * q3),
        1 - 2 * (q1 * q1 + q2 * q2)
    )

    pitch_value = 2 * (q0 * q2 - q3 * q1)
    pitch_value = np.clip(pitch_value, -1.0, 1.0)

    pitch = np.arcsin(pitch_value)

    yaw = np.arctan2(
        2 * (q0 * q3 + q1 * q2),
        1 - 2 * (q2 * q2 + q3 * q3)
    )

    return roll, pitch, yaw


base["roll"], base["pitch"], base["yaw"] = zip(
    *base.apply(
        lambda r: quaternion_to_euler(
            r["q0"],
            r["q1"],
            r["q2"],
            r["q3"]
        ),
        axis=1
    )
)

# Remove quaternion columns
base = base.drop(
    columns=["q0", "q1", "q2", "q3"]
)

# Save
os.makedirs("data_attack01", exist_ok=True)

base.to_csv(
    output_path,
    index=False
)

print("\n========================================")
print("ATTACK 01 EXTRACTION COMPLETE")
print("========================================")
print("Rows:", len(base))
print("Columns:", len(base.columns))
print("Duration:", round(base["time_sec"].iloc[-1], 2), "seconds")
print("Output:", output_path)
print("========================================")
