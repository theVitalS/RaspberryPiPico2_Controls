from machine import Pin, PWM
import time
from car import *
from dumzy_listner import start_signal_listener, get_latest_command
from arm import *
import _thread

DETAILED_CONTROL = True

def motors_thread(to_print=True, timeout=300):
    time.sleep(2)
    print((('-' * 30) + '\n') * 100)

    control_mode = 1
    print((('=' * 30) + '\n') * 100)
    start_time = time.time()
    while time.time() - start_time < timeout:
        print(f'rolling {time.time() - start_time}')
        b, y, x = get_latest_command()

        if not (b == 0 and x == 50 and y == 50):
            start_time = time.time()

        print(f'Rolling for: {b=}, {y=}, {x=}')
        move(x, y, DETAILED_CONTROL)

        control_mode = arm_control(servos, control_mode, b)
        time.sleep(0.05)

def control_loop(to_print=True):
    stop()
    start_signal_listener()
    motors_thread()

stop()
time.sleep(3)

if __name__ == '__main__':
    control_loop(to_print=True)

