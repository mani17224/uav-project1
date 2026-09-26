import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("WAITING FOR PX4...")

    async for state in drone.core.connection_state():
        print("PX4 CONNECTED:", state.is_connected)
        if state.is_connected:
            break

asyncio.run(main())
