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

    print("Waiting for actuator output message...")

    async for motors in drone.telemetry.actuator_output_status():
        print("ACTIVE:", motors.active)
        print("ACTUATOR:", motors.actuator)
        print("TYPE:", type(motors.actuator))

        if len(motors.actuator) >= 4:
            print(
                "motor_1 =", motors.actuator[0],
                "motor_2 =", motors.actuator[1],
                "motor_3 =", motors.actuator[2],
                "motor_4 =", motors.actuator[3]
            )

        break


if __name__ == "__main__":
    asyncio.run(main())
