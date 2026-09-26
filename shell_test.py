import asyncio
from mavsdk import System

async def main():
    drone = System()

    print("Connecting to PX4...")
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            break

    print("Running: shell API inspection")
    
    pass

    print("Command sent!")

if __name__ == "__main__":
    asyncio.run(main())
