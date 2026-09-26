import asyncio
import time

from mavsdk import System
from mavsdk.offboard import VelocityNedYaw
from mavsdk.failure import FailureUnit, FailureType


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

    print("========================================")
    print("   UAV ATTACK 01 - GPS WRONG INJECTION")
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

    # ====================================
    # NORMAL PHASE
    # ====================================

    print("\n========== NORMAL PHASE ==========")

    await hover(drone, 10)

    await move(
        drone,
        "FORWARD",
        1.0,
        0.0,
        5
    )

    await hover(drone, 10)

    # ====================================
    # START OFFBOARD
    # ====================================

    print("\nPreparing Offboard mode...")

    await set_velocity(
        drone,
        0.0,
        0.0,
        0.0
    )

    await drone.offboard.start()

    print("OFFBOARD STARTED!")

    # ====================================
    # PRE-ATTACK NORMAL DATA
    # ====================================

    print("\n========== PRE-ATTACK ==========")

    await hover(drone, 10)

    # ====================================
    # GPS ATTACK
    # ====================================

    print("\n========================================")
    print("       GPS ATTACK STARTING")
    print("========================================")

    attack_start = time.time()

    print(f"Attack start time: {attack_start:.3f}")

    print("Injecting GPS WRONG...")

    await drone.failure.inject(
        FailureUnit.SENSOR_GPS,
        FailureType.WRONG,
        0
    )

    print("GPS WRONG INJECTED!")

    print("Collecting attack telemetry for 10 seconds...")

    await hover(drone, 10)

    attack_end = time.time()

    print(f"Attack end time: {attack_end:.3f}")
    print(
        f"Attack duration: "
        f"{attack_end - attack_start:.2f} seconds"
    )

    # ====================================
    # GPS RECOVERY
    # ====================================

    print("\n========================================")
    print("       GPS RECOVERY")
    print("========================================")

    print("Restoring GPS...")

    await drone.failure.inject(
        FailureUnit.SENSOR_GPS,
        FailureType.OK,
        0
    )

    recovery_start = time.time()

    print("GPS RESTORED!")

    print("Collecting recovery telemetry for 10 seconds...")

    await hover(drone, 10)

    recovery_end = time.time()

    print(
        f"Recovery duration: "
        f"{recovery_end - recovery_start:.2f} seconds"
    )

    # ====================================
    # POST ATTACK
    # ====================================

    print("\n========== POST-ATTACK ==========")

    await move(
        drone,
        "BACKWARD",
        -1.0,
        0.0,
        5
    )

    await hover(drone, 10)

    # ====================================
    # LAND
    # ====================================

    print("\nStopping Offboard mode...")

    await drone.offboard.stop()

    print("Landing...")

    await drone.action.land()

    await wait_until_landed(drone)

    print("\n========================================")
    print("      ATTACK 01 COMPLETED")
    print("========================================")
    print("GPS WRONG injection experiment finished.")


if __name__ == "__main__":
    asyncio.run(main())
