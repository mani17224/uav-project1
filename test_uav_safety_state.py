import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("WAITING FOR PX4...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED: True")
            break

    async for armed in drone.telemetry.armed():
        print("ARMED:", armed)
        break

    async for mode in drone.telemetry.flight_mode():
        print("FLIGHT MODE:", mode)
        break

asyncio.run(main())
