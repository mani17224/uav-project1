import asyncio
from mavsdk import System


async def main():
    drone = System()

    print("Connecting to PX4...")
    await drone.connect(
        system_address="udpin://0.0.0.0:14540"
    )

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            break

    print("Reading angular velocity...")

    async for angular in drone.telemetry.attitude_angular_velocity_body():
        print(
            f"angular_x={angular.roll_rad_s:.4f} rad/s, "
            f"angular_y={angular.pitch_rad_s:.4f} rad/s, "
            f"angular_z={angular.yaw_rad_s:.4f} rad/s"
        )
        break


if __name__ == "__main__":
    asyncio.run(main())
