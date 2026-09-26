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

    print("CURRENT FLIGHT MODE:")

    async for mode in drone.telemetry.flight_mode():
        print(mode)
        break

    print("SENDING HOLD COMMAND...")

    try:
        await drone.action.hold()
        print("HOLD COMMAND SENT")
    except Exception as e:
        print("HOLD COMMAND ERROR:", e)

asyncio.run(main())
