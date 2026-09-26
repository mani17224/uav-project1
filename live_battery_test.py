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

    print("Reading battery telemetry...")

    async for battery in drone.telemetry.battery():
        print(
            f"voltage_v={battery.voltage_v:.3f} V, "
            f"remaining={battery.remaining_percent:.1f}%"
        )
        break


if __name__ == "__main__":
    asyncio.run(main())
