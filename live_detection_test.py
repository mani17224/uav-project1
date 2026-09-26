import asyncio
from collections import deque

import numpy as np
import joblib
import pandas as pd
from mavsdk import System

from dashboard.detector import detect


WINDOW_SIZE = 20

SCALER_PATH = "processed_data/standard_scaler.pkl"
scaler = joblib.load(SCALER_PATH)
print("StandardScaler loaded:", SCALER_PATH)


class LiveTelemetry:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0

        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0

        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

        self.angular_x = 0.0
        self.angular_y = 0.0
        self.angular_z = 0.0

        self.voltage_v = 0.0
        self.remaining = 0.0

        self.motor_1 = 0.0
        self.motor_2 = 0.0
        self.motor_3 = 0.0
        self.motor_4 = 0.0


def get_feature_vector(t):
    return np.array([
        t.x,
        t.y,
        t.z,
        t.vx,
        t.vy,
        t.vz,
        t.ax,
        t.ay,
        t.az,
        t.roll,
        t.pitch,
        t.yaw,
        t.angular_x,
        t.angular_y,
        t.angular_z,
        t.voltage_v,
        t.remaining,
        t.motor_1,
        t.motor_2,
        t.motor_3,
        t.motor_4,
    ], dtype=np.float32)


async def position_velocity_task(drone, telemetry):
    async for pv in drone.telemetry.position_velocity_ned():
        telemetry.x = pv.position.north_m
        telemetry.y = pv.position.east_m
        telemetry.z = pv.position.down_m

        telemetry.vx = pv.velocity.north_m_s
        telemetry.vy = pv.velocity.east_m_s
        telemetry.vz = pv.velocity.down_m_s


async def imu_task(drone, telemetry):
    async for imu in drone.telemetry.imu():
        telemetry.ax = imu.acceleration_frd.forward_m_s2
        telemetry.ay = imu.acceleration_frd.right_m_s2
        telemetry.az = imu.acceleration_frd.down_m_s2


async def attitude_task(drone, telemetry):
    async for attitude in drone.telemetry.attitude_euler():
        telemetry.roll = attitude.roll_deg
        telemetry.pitch = attitude.pitch_deg
        telemetry.yaw = attitude.yaw_deg


async def angular_velocity_task(drone, telemetry):
    async for angular in drone.telemetry.attitude_angular_velocity_body():
        telemetry.angular_x = angular.roll_rad_s
        telemetry.angular_y = angular.pitch_rad_s
        telemetry.angular_z = angular.yaw_rad_s


async def battery_task(drone, telemetry):
    async for battery in drone.telemetry.battery():
        telemetry.voltage_v = battery.voltage_v
        telemetry.remaining = battery.remaining_percent / 100.0

def scale_window(raw_window, time_values):
    raw_window = np.asarray(raw_window, dtype=np.float32)

    if raw_window.shape != (20, 21):
        raise ValueError(
            f"Expected raw window shape (20, 21), got {raw_window.shape}"
        )

    time_values = np.asarray(time_values, dtype=np.float32).reshape(20, 1)

    scaler_input = np.concatenate(
        [raw_window, time_values],
        axis=1
    )

    scaled = scaler.transform(pd.DataFrame(scaler_input, columns=scaler.feature_names_in_))

    return scaled[:, :21].astype(np.float32)

async def motor_task(drone, telemetry):
    """
    Read live motor values from PX4 through the MAVSDK Shell.
    PX4 command: listener actuator_motors
    """

    async def receive_output():
        buffer = ""

        async for data in drone.shell.receive():
            buffer += data

            if "control:" not in buffer:
                continue

            start = buffer.find("control:")
            line_part = buffer[start:]

            if "[" not in line_part or "]" not in line_part:
                continue

            values_text = line_part.split("[", 1)[1].split("]", 1)[0]
            values = values_text.split(",")

            try:
                motors = [float(v.strip()) for v in values[:4]]

                telemetry.motor_1 = motors[0]
                telemetry.motor_2 = motors[1]
                telemetry.motor_3 = motors[2]
                telemetry.motor_4 = motors[3]

                print(
                    f"MOTORS: "
                    f"{motors[0]:.4f}, "
                    f"{motors[1]:.4f}, "
                    f"{motors[2]:.4f}, "
                    f"{motors[3]:.4f}"
                )

                buffer = ""
                
            except ValueError:
                pass

    receiver = asyncio.create_task(receive_output())

    await asyncio.sleep(1)

    await drone.shell.send("listener actuator_motors\n")

    await receiver

async def main():
    start_time = asyncio.get_running_loop().time()

    drone = System()
    telemetry = LiveTelemetry()

    window = deque(maxlen=WINDOW_SIZE)
    time_window = deque(maxlen=WINDOW_SIZE)
    detection_windows = 0
    WARMUP_WINDOWS = 5

    print("========================================")
    print("       LIVE AI DETECTION TEST")
    print("========================================")

    print("Connecting to PX4...")

    await drone.connect(
        system_address="udpin://0.0.0.0:14540"
    )

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            break

    print("Collecting live telemetry...")
    print("Building 20 x 21 ML window...")
    print()

    tasks = [
        asyncio.create_task(
            position_velocity_task(drone, telemetry)
        ),
        asyncio.create_task(
            imu_task(drone, telemetry)
        ),
        asyncio.create_task(
            attitude_task(drone, telemetry)
        ),
        asyncio.create_task(
            angular_velocity_task(drone, telemetry)
        ),
        asyncio.create_task(
            battery_task(drone, telemetry)
        ),
        asyncio.create_task(
            motor_task(drone, telemetry)
        ),
    ]

    try:
        while True:

            await asyncio.sleep(0.1)

            features = get_feature_vector(telemetry)

            window.append(features)
            time_window.append(asyncio.get_running_loop().time() - start_time)

            print(
                f"Buffer: {len(window):2d}/{WINDOW_SIZE} | "
                f"vx={telemetry.vx:6.3f} | "
                f"vy={telemetry.vy:6.3f} | "
                f"vz={telemetry.vz:6.3f}"
            )

            if len(window) == WINDOW_SIZE:

                raw_X = np.array(window, dtype=np.float32)
                time_X = np.array(time_window, dtype=np.float32)
                X = scale_window(raw_X, time_X)

                print()
                print("----------------------------------------")
                print("20 x 21 WINDOW READY")
                print("Shape:", X.shape)

                detection_windows += 1

                if detection_windows <= WARMUP_WINDOWS:
                    print(f"Warm-up window {detection_windows}/{WARMUP_WINDOWS} — stabilizing telemetry...")
                    print("Detection: WARM-UP")
                    print("----------------------------------------")
                    print()
                    continue

                result = detect(X)

                print(
                    f"Anomaly Score : {result['score']:.4f}"
                )

                print(
                    f"Threshold     : {result['threshold']:.4f}"
                )

                print(
                    f"Detection     : {result['status']}"
                )

                print("----------------------------------------")
                print()

    except KeyboardInterrupt:
        print("\nLive detection stopped.")

    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True
        )


if __name__ == "__main__":
    asyncio.run(main())