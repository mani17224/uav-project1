from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class UAVState:
    timestamp: Optional[float] = None

    # Position
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # Linear velocity
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0

    # Attitude
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    # Battery
    voltage_v: float = 0.0
    battery_remaining: float | None = None

    # Navigation / flight state
    gps_valid: bool = True
    flight_mode: str = "UNKNOWN"
    armed: bool = False

    def speed(self):
        return (self.vx**2 + self.vy**2 + self.vz**2) ** 0.5

    def altitude(self):
        return abs(self.z)

    def to_dict(self):
        data = asdict(self)
        data["speed"] = self.speed()
        data["altitude"] = self.altitude()
        return data
