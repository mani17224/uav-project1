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

    print("Failure API functions:")
    print([
        x for x in dir(drone.failure)
        if not x.startswith("_")
    ])


if __name__ == "__main__":
    asyncio.run(main())
