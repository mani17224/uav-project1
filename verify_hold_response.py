import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED: True")
            break

    async for mode in drone.telemetry.flight_mode():
        print("ACTUAL PX4 FLIGHT MODE:", mode)
        print("HOLD VERIFIED:", str(mode) == "HOLD")
        break

asyncio.run(main())
