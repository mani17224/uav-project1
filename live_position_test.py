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

    print("Reading position and velocity...")

    async for pv in drone.telemetry.position_velocity_ned():
        print(
            f"x={pv.position.north_m:.3f}, "
            f"y={pv.position.east_m:.3f}, "
            f"z={pv.position.down_m:.3f}, "
            f"vx={pv.velocity.north_m_s:.3f}, "
            f"vy={pv.velocity.east_m_s:.3f}, "
            f"vz={pv.velocity.down_m_s:.3f}"
        )
        break


if __name__ == "__main__":
    asyncio.run(main())
