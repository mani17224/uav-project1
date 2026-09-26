import asyncio
from mavsdk import System
from mavsdk.failure import FailureUnit, FailureType


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

    print("Injecting GPS WRONG...")
    await drone.failure.inject(
        FailureUnit.SENSOR_GPS,
        FailureType.WRONG,
        0
    )

    print("GPS WRONG injected.")

    await asyncio.sleep(5)

    print("Restoring GPS...")
    await drone.failure.inject(
        FailureUnit.SENSOR_GPS,
        FailureType.OK,
        0
    )

    print("GPS restored.")


if __name__ == "__main__":
    asyncio.run(main())
