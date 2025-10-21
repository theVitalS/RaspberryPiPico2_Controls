from machine import time_pulse_us
import time
from dumzy_listner import start_signal_listener, get_latest_command
from arm import *
from car import MotorController
import _thread

motor = MotorController(detailed_control=True, debug=False)

def motors_thread(timeout=300):
    print('Motors thread started')
    time.sleep(2)
    control_mode = 1
    start_time = time.time()
    lsst_switch = start_time

    while time.time() - start_time < timeout:
        command = get_latest_command()
        b, y, x = command

        if not (b == 0 and x == 50 and y == 50):
            start_time = time.time()

        if motor.debug:
            print(f'[Main] Command received: {b=}, {y=}, {x=}')
        motor.move(x, y)
        if b != 5:
            arm_control(servos, control_mode, b)
        elif time.time() - lsst_switch > 1:
            control_mode *= -1
            lsst_switch = time.time()
            if motor.debug:
                print(f'[Main] Control mode switched: {control_mode}')

        time.sleep(0.05)

def control_loop():
    motor.stop()
    start_signal_listener()
    motors_thread()

motor.stop()


if __name__ == '__main__':
    control_loop()

