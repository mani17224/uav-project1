import asyncio
from mavsdk import System


async def main():
    drone = System()

    print("Connecting to PX4...")
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for PX4 connection...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            break

    print("Waiting for telemetry...")

    async for position in drone.telemetry.position():
        print(
            f"Latitude: {position.latitude_deg:.6f}, "
            f"Longitude: {position.longitude_deg:.6f}, "
            f"Relative Altitude: {position.relative_altitude_m:.2f} m"
        )
        break


if __name__ == "__main__":
    asyncio.run(main())
