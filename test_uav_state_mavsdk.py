import asyncio
from mavsdk import System
from security.uav_state import UAVState

async def main():
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("WAITING FOR PX4...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED: True")
            break

    async for position in drone.telemetry.position():
        async for velocity in drone.telemetry.velocity_ned():
            uav = UAVState(
                timestamp=0.0,
                x=0.0,
                y=0.0,
                z=position.relative_altitude_m,
                vx=velocity.north_m_s,
                vy=velocity.east_m_s,
                vz=velocity.down_m_s,
                gps_valid=True,
            )

            print("UAV STATE CREATED")
            print("Altitude:", uav.altitude())
            print("Speed:", uav.speed())
            print("GPS Valid:", uav.gps_valid)
            return

asyncio.run(main())
