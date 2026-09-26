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

    async for armed in drone.telemetry.armed():
        print("ARMED:", armed)
        break

    async for mode in drone.telemetry.flight_mode():
        print("CURRENT FLIGHT MODE:", mode)
        break

    print("SENDING RTL COMMAND...")

    try:
        await drone.action.return_to_launch()
        print("RTL COMMAND SENT")
    except Exception as e:
        print("RTL COMMAND ERROR:", e)

asyncio.run(main())
