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

    print("Reading attitude...")

    async for attitude in drone.telemetry.attitude_euler():
        print(
            f"roll={attitude.roll_deg:.3f} deg, "
            f"pitch={attitude.pitch_deg:.3f} deg, "
            f"yaw={attitude.yaw_deg:.3f} deg"
        )
        break


if __name__ == "__main__":
    asyncio.run(main())
