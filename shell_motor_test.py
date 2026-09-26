import asyncio
from mavsdk import System

async def main():
    drone = System()

    print("Connecting to PX4...")
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("PX4 CONNECTED!")
            break

    print("Starting shell receive...")
    
    async def receive_shell():
        async for data in drone.shell.receive():
            print("PX4:", repr(data))

    receiver = asyncio.create_task(receive_shell())

    await asyncio.sleep(1)

    print("Sending: listener actuator_motors")
    await drone.shell.send("listener actuator_motors\n")

    await asyncio.sleep(5)

    receiver.cancel()

if __name__ == "__main__":
    asyncio.run(main())
