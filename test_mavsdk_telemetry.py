import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("WAITING FOR PX4...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED: True")
            break

    async for position in drone.telemetry.position():
        print("LATITUDE:", position.latitude_deg)
        print("LONGITUDE:", position.longitude_deg)
        print("ALTITUDE:", position.relative_altitude_m)
        break

    async for velocity in drone.telemetry.velocity_ned():
        print("VELOCITY NORTH:", velocity.north_m_s)
        print("VELOCITY EAST:", velocity.east_m_s)
        print("VELOCITY DOWN:", velocity.down_m_s)
        break

asyncio.run(main())
