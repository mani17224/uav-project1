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


async def move(drone, name, north, east, seconds):
    print(f"Moving {name} for {seconds} seconds...")

    await set_velocity(drone, north, east, 0.0)

    await asyncio.sleep(seconds)


async def main():

    drone = System()

    # --------------------------------------------------
    # 1. CONNECT TO PX4
    # --------------------------------------------------

    print("========================================")
    print("      UAV NORMAL FLIGHT TEST")
    print("========================================")

    print("Connecting to PX4...")

    await drone.connect(
        system_address="udpin://0.0.0.0:14540"
    )

    await wait_until_connected(drone)

    # --------------------------------------------------
    # 2. WAIT FOR PX4 READY
    # --------------------------------------------------

    await wait_until_ready(drone)

    # --------------------------------------------------
    # 3. ARM
    # --------------------------------------------------

    print("Arming...")

    await drone.action.arm()

    print("ARM SUCCESSFUL!")

    # --------------------------------------------------
    # 4. TAKEOFF
    # --------------------------------------------------

    print("Taking off...")

    await drone.action.takeoff()

    # --------------------------------------------------
    # 5. VERIFY AIRBORNE
    # --------------------------------------------------

    await wait_until_airborne(drone)

    # --------------------------------------------------
    # 6. INITIAL HOVER
    # --------------------------------------------------

    await hover(drone, 10)

    # --------------------------------------------------
    # 7. START OFFBOARD
    # --------------------------------------------------

    print("Preparing Offboard mode...")

    # PX4 requires an initial setpoint before
    # Offboard mode is started.

    await set_velocity(
        drone,
        0.0,
        0.0,
        0.0
    )

    print("Starting Offboard mode...")

    await drone.offboard.start()

    print("OFFBOARD STARTED!")

    # --------------------------------------------------
    # 8. FORWARD
    # --------------------------------------------------

    await move(
        drone,
        "FORWARD",
        1.0,
        0.0,
        5
    )

    # --------------------------------------------------
    # 9. HOVER
    # --------------------------------------------------

    await hover(drone, 10)

    # --------------------------------------------------
    # 10. RIGHT
    # --------------------------------------------------

    await move(
        drone,
        "RIGHT",
        0.0,
        1.0,
        5
    )

    # --------------------------------------------------
    # 11. HOVER
    # --------------------------------------------------

    await hover(drone, 10)

    # --------------------------------------------------
    # 12. LEFT
    # --------------------------------------------------

    await move(
        drone,
        "LEFT",
        0.0,
        -1.0,
        5
    )

    # --------------------------------------------------
    # 13. HOVER
    # --------------------------------------------------

    await hover(drone, 10)

    # --------------------------------------------------
    # 14. BACKWARD
    # --------------------------------------------------

    await move(
        drone,
        "BACKWARD",
        -1.0,
        0.0,
        5
    )

    # --------------------------------------------------
    # 15. FINAL HOVER
    # --------------------------------------------------

    await hover(drone, 10)

    # --------------------------------------------------
    # 16. STOP OFFBOARD
    # --------------------------------------------------

    print("Stopping Offboard mode...")

    await drone.offboard.stop()

    print("OFFBOARD STOPPED!")

    # --------------------------------------------------
    # 17. LAND
    # --------------------------------------------------

    print("Landing...")

    await drone.action.land()

    # --------------------------------------------------
    # 18. VERIFY LANDING
    # --------------------------------------------------

    await wait_until_landed(drone)

    # --------------------------------------------------
    # 19. COMPLETE
    # --------------------------------------------------

    print("========================================")
    print("      FLIGHT COMPLETED SUCCESSFULLY")
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())
