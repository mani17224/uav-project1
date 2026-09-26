import asyncio
from mavsdk import System


async def main():
    drone = System()

    print("Connecting to PX4...")

    await drone.connect(system_address="udp://:14540")

    print("Waiting for PX4...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            break


if __name__ == "__main__":
    asyncio.run(main())
