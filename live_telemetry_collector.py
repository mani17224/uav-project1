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

    print("Collecting live telemetry...")
    print("Press Ctrl+C to stop.")
    print()

    async for pv in drone.telemetry.position_velocity_ned():
        print(
            f"x={pv.position.north_m:.2f}, "
            f"y={pv.position.east_m:.2f}, "
            f"z={pv.position.down_m:.2f}, "
            f"vx={pv.velocity.north_m_s:.2f}, "
            f"vy={pv.velocity.east_m_s:.2f}, "
            f"vz={pv.velocity.down_m_s:.2f}"
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTelemetry collector stopped.")
