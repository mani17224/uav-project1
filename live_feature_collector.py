import asyncio
from mavsdk import System


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
        telemetry.remaining = battery.remaining_percent


async def main():

    drone = System()
    telemetry = LiveTelemetry()

    print("Connecting to PX4...")

    await drone.connect(
        system_address="udpin://0.0.0.0:14540"
    )

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            break

    print("Starting live telemetry streams...")

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
    ]

    try:
        while True:
            await asyncio.sleep(1)

            print(
                f"x={telemetry.x:.2f}, "
                f"y={telemetry.y:.2f}, "
                f"z={telemetry.z:.2f} | "
                f"vx={telemetry.vx:.2f}, "
                f"vy={telemetry.vy:.2f}, "
                f"vz={telemetry.vz:.2f} | "
                f"voltage={telemetry.voltage_v:.2f}V | "
                f"battery={telemetry.remaining:.1f}%"
            )

    except KeyboardInterrupt:
        print("\nStopping telemetry...")

    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True
        )


if __name__ == "__main__":
    asyncio.run(main())
