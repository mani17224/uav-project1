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

    print("Reading acceleration...")

    async for acceleration in drone.telemetry.imu():
        print(
            f"ax={acceleration.acceleration_frd.forward_m_s2:.3f}, "
            f"ay={acceleration.acceleration_frd.right_m_s2:.3f}, "
            f"az={acceleration.acceleration_frd.down_m_s2:.3f}"
        )
        break


if __name__ == "__main__":
    asyncio.run(main())
