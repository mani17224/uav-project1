import asyncio
import threading
from collections import deque
from dataclasses import dataclass, asdict

import joblib
import numpy as np
import pandas as pd
import csv
from datetime import datetime
from mavsdk import System

from detector import detect


WINDOW_SIZE = 20
WARMUP_WINDOWS = 5
CONSECUTIVE_ANOMALY_WINDOWS = 20

BASE_DIR = __import__("pathlib").Path(__file__).resolve().parent.parent
SCALER_PATH = BASE_DIR / "processed_data" / "standard_scaler.pkl"
LIVE_LOG_PATH = BASE_DIR / "processed_data" / "live_detection_log.csv"

scaler = joblib.load(SCALER_PATH)


@dataclass
class LiveState:
    connected: bool = False
    status: str = "STARTING"
    score: float = 0.0
    threshold: float = 0.0
    peak_score: float = 0.0
    last_detection: str = "None"
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    az: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    angular_x: float = 0.0
    angular_y: float = 0.0
    angular_z: float = 0.0
    voltage_v: float = 0.0
    remaining: float = 0.0
    motor_1: float = 0.0
    motor_2: float = 0.0
    motor_3: float = 0.0
    motor_4: float = 0.0
    buffer_size: int = 0
    warmup: bool = True


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


state = LiveState()
state_lock = threading.Lock()


def update_state(**kwargs):
    with state_lock:
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)


def get_state():
    with state_lock:
        return asdict(state)


def log_detection(timestamp, raw_status, confirmed_status, score, threshold, telemetry):
    file_exists = LIVE_LOG_PATH.exists()
    with open(LIVE_LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "raw_status", "confirmed_status", "score", "threshold",
                "x", "y", "z", "vx", "vy", "vz"
            ])
        writer.writerow([
            timestamp, raw_status, confirmed_status,
            f"{score:.6f}", f"{threshold:.6f}",
            f"{telemetry.x:.6f}", f"{telemetry.y:.6f}", f"{telemetry.z:.6f}",
            f"{telemetry.vx:.6f}", f"{telemetry.vy:.6f}", f"{telemetry.vz:.6f}"
        ])


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


def scale_window(raw_window, time_values):
    raw_window = np.asarray(raw_window, dtype=np.float32)

    time_values = np.asarray(
        time_values,
        dtype=np.float32
    ).reshape(WINDOW_SIZE, 1)

    scaler_input = np.concatenate(
        [raw_window, time_values],
        axis=1
    )

    scaled = scaler.transform(
        pd.DataFrame(
            scaler_input,
            columns=scaler.feature_names_in_
        )
    )

    return scaled[:, :21].astype(np.float32)


async def position_velocity_task(drone, telemetry):
    async for position_velocity in drone.telemetry.position_velocity_ned():
        telemetry.x = position_velocity.position.north_m
        telemetry.y = position_velocity.position.east_m
        telemetry.z = position_velocity.position.down_m

        telemetry.vx = position_velocity.velocity.north_m_s
        telemetry.vy = position_velocity.velocity.east_m_s
        telemetry.vz = position_velocity.velocity.down_m_s


async def shell_telemetry_task(drone, telemetry):
    """
    Read PX4 vehicle_local_position and actuator_motors through one
    shared MAVSDK Shell receiver.

    A single receiver avoids concurrent drone.shell.receive() consumers.
    Both listener commands are one-shot snapshots and are requested
    periodically.
    """
    buffer = ""

    async def receive_output():
        nonlocal buffer

        import re

        async for data in drone.shell.receive():
            buffer += data

            # -----------------------------
            # vehicle_local_position
            # -----------------------------
            ax_match = re.search(r"\bax:\s*([-+]?\d*\.?\d+)", buffer)
            ay_match = re.search(r"\bay:\s*([-+]?\d*\.?\d+)", buffer)
            az_match = re.search(r"\baz:\s*([-+]?\d*\.?\d+)", buffer)

            if ax_match and ay_match and az_match:
                telemetry.ax = float(ax_match.group(1))
                telemetry.ay = float(ay_match.group(1))
                telemetry.az = float(az_match.group(1))

                buffer = buffer[az_match.end():]

            # -----------------------------
            # actuator_motors
            # -----------------------------
            control_match = re.search(
                r"control:\s*\[([^\]]+)\]",
                buffer
            )

            if control_match:
                try:
                    values = control_match.group(1).split(",")
                    motors = [float(v.strip()) for v in values[:4]]

                    if len(motors) == 4:
                        telemetry.motor_1 = motors[0]
                        telemetry.motor_2 = motors[1]
                        telemetry.motor_3 = motors[2]
                        telemetry.motor_4 = motors[3]

                    buffer = buffer[control_match.end():]

                except ValueError:
                    pass

    receiver = asyncio.create_task(receive_output())

    await asyncio.sleep(1)

    try:
        while True:
            # One-shot PX4 snapshots.
            await drone.shell.send("listener vehicle_local_position 1")
            await asyncio.sleep(0.15)

            await drone.shell.send("listener actuator_motors 1")
            await asyncio.sleep(0.15)

    except asyncio.CancelledError:
        receiver.cancel()
        raise



async def attitude_task(drone, telemetry):
    # MAVSDK provides Euler angles in degrees.
    # Training data uses radians, so convert degrees to radians.
    async for attitude in drone.telemetry.attitude_euler():
        telemetry.roll = np.deg2rad(attitude.roll_deg)
        telemetry.pitch = np.deg2rad(attitude.pitch_deg)
        telemetry.yaw = np.deg2rad(attitude.yaw_deg)


async def angular_velocity_task(drone, telemetry):
    # MAVSDK provides body angular velocity directly in rad/s.
    async for angular in drone.telemetry.attitude_angular_velocity_body():
        telemetry.angular_x = angular.roll_rad_s
        telemetry.angular_y = angular.pitch_rad_s
        telemetry.angular_z = angular.yaw_rad_s


async def battery_task(drone, telemetry):
    async for battery in drone.telemetry.battery():
        telemetry.voltage_v = battery.voltage_v
        telemetry.remaining = battery.remaining_percent / 100.0


async def detector_loop():
    global state

    start_time = asyncio.get_running_loop().time()

    drone = System()
    telemetry = LiveTelemetry()

    window = deque(maxlen=WINDOW_SIZE)
    time_window = deque(maxlen=WINDOW_SIZE)

    await drone.connect(
        system_address="udpin://0.0.0.0:14540"
    )

    async for connection in drone.core.connection_state():
        if connection.is_connected:
            update_state(
                connected=True,
                status="WARM-UP"
            )
            break

    tasks = [
        asyncio.create_task(
            position_velocity_task(drone, telemetry)
        ),
        asyncio.create_task(
            shell_telemetry_task(drone, telemetry)
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
    ]

    detection_windows = 0
    anomaly_streak = 0

    try:
        while True:
            await asyncio.sleep(0.1)

            features = get_feature_vector(telemetry)

            window.append(features)
            time_window.append(
                asyncio.get_running_loop().time() - start_time
            )

            update_state(
                x=float(telemetry.x),
                y=float(telemetry.y),
                z=float(telemetry.z),
                vx=float(telemetry.vx),
                vy=float(telemetry.vy),
                vz=float(telemetry.vz),
                ax=float(telemetry.ax),
                ay=float(telemetry.ay),
                az=float(telemetry.az),
                roll=float(telemetry.roll),
                pitch=float(telemetry.pitch),
                yaw=float(telemetry.yaw),
                angular_x=float(telemetry.angular_x),
                angular_y=float(telemetry.angular_y),
                angular_z=float(telemetry.angular_z),
                voltage_v=float(telemetry.voltage_v),
                remaining=float(telemetry.remaining),
                motor_1=float(telemetry.motor_1),
                motor_2=float(telemetry.motor_2),
                motor_3=float(telemetry.motor_3),
                motor_4=float(telemetry.motor_4),
                buffer_size=len(window)
            )

            if len(window) < WINDOW_SIZE:
                continue

            raw_X = np.array(
                window,
                dtype=np.float32
            )

            time_X = np.array(
                time_window,
                dtype=np.float32
            )

            X = scale_window(
                raw_X,
                time_X
            )

            detection_windows += 1

            if detection_windows <= WARMUP_WINDOWS:
                update_state(
                    status="WARM-UP",
                    warmup=True
                )
                continue

            result = detect(X)

            current_score = float(result["score"])
            current_threshold = float(result["threshold"])

            if result["status"] == "ANOMALY":
                anomaly_streak += 1
            else:
                anomaly_streak = 0

            confirmed_status = (
                "ANOMALY"
                if anomaly_streak >= CONSECUTIVE_ANOMALY_WINDOWS
                else "NORMAL"
            )

            if confirmed_status == "ANOMALY":
                update_state(last_detection="ANOMALY DETECTED")

            log_detection(
                datetime.now().isoformat(),
                result["status"],
                confirmed_status,
                current_score,
                current_threshold,
                telemetry
            )

            update_state(
                peak_score=max(state.peak_score, current_score),
                status=confirmed_status,
                score=current_score,
                threshold=current_threshold,
                warmup=False
            )

    except asyncio.CancelledError:
        pass

    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True
        )


def start_live_detector():
    thread = threading.Thread(
        target=lambda: asyncio.run(detector_loop()),
        daemon=True
    )

    thread.start()

    return thread
