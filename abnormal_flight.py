import asyncio

from mavsdk import System
from mavsdk.offboard import VelocityNedYaw


async def wait_until_connected(drone):
    print("Waiting for PX4 connection...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            return


async def wait_until_ready(drone):
    print("Waiting for PX4 to be ready...")

    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("PX4 READY!")
            return


async def wait_until_airborne(drone):
    print("Waiting for UAV to become airborne...")

    async for in_air in drone.telemetry.in_air():
        if in_air:
            print("UAV IS AIRBORNE!")
            return


async def wait_until_landed(drone):
    print("Waiting for landing...")

    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("LANDED!")
            return


async def set_velocity(drone, north, east, down, yaw=0.0):
    await drone.offboard.set_velocity_ned(
        VelocityNedYaw(north, east, down, yaw)
    )


async def hover(drone, seconds):
    print(f"Hovering for {seconds} seconds...")

    await set_velocity(drone, 0.0, 0.0, 0.0)

    await asyncio.sleep(seconds)


async def abnormal_movement(drone):
    print()
    print("########################################")
    print("   ABNORMAL MOVEMENT SCENARIO")
    print("########################################")

    print("Sudden NORTH movement...")
    await set_velocity(drone, 5.0, 0.0, 0.0)
    await asyncio.sleep(3)

    print("Sudden EAST movement...")
    await set_velocity(drone, 0.0, 5.0, 0.0)
    await asyncio.sleep(3)

    print("Sudden SOUTH movement...")
    await set_velocity(drone, -5.0, 0.0, 0.0)
    await asyncio.sleep(3)

    print("Sudden WEST movement...")
    await set_velocity(drone, 0.0, -5.0, 0.0)
    await asyncio.sleep(3)

    print("Stopping abnormal movement...")
    await set_velocity(drone, 0.0, 0.0, 0.0)


async def main():

    drone = System()

    print("========================================")
    print("     UAV ABNORMAL FLIGHT TEST")
    print("========================================")

    print("Connecting to PX4...")

    await drone.connect(
        system_address="udpin://0.0.0.0:14540"
    )

    await wait_until_connected(drone)
    await wait_until_ready(drone)

    print("Arming...")
    await drone.action.arm()
    print("ARM SUCCESSFUL!")

    print("Taking off...")
    await drone.action.takeoff()

    await wait_until_airborne(drone)

    await hover(drone, 10)

    print("Preparing Offboard mode...")
    await set_velocity(
        drone,
        0.0,
        0.0,
        0.0
    )

    print("Starting Offboard mode...")
    await drone.offboard.start()

    print("OFFBOARD STARTED!")

    await abnormal_movement(drone)

    await hover(drone, 5)

    print("Stopping Offboard mode...")
    await drone.offboard.stop()

    print("Landing...")
    await drone.action.land()

    await wait_until_landed(drone)

    print("========================================")
    print("   ABNORMAL FLIGHT COMPLETED")
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())
