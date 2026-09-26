import asyncio
from mavsdk import System


async def main():
    drone = System()

    print("Connecting to PX4...")
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for PX4...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            break

    print("Waiting for PX4 to be ready...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("PX4 READY!")
            break

    print("Arming...")
    await drone.action.arm()
    print("ARM SUCCESSFUL!")

    print("Taking off...")
    await drone.action.takeoff()

    print("Hovering for 10 seconds...")
    await asyncio.sleep(10)

    print("Landing...")
    await drone.action.land()

    print("Waiting for landing...")
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("LANDED!")
            break


if __name__ == "__main__":
    asyncio.run(main())
