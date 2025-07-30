from machine import Pin, PWM
import random
import time
import utime
from car import *
from dumzy_listner import *
from arm import *
import _thread
import machine

# Global variables
DETAILED_CONTROL = True

def signal_thread(to_print=True, timeout=600, retries=2):
    time.sleep(1)
    global command
    global control_mode

    control_mode = 1
    command = [0, 50, 50]
    start_time = time.time()
    nrf = initiate_nrf(retries=5)
    i = 0
    while nrf is None:
        command = [0, 50, 50]
        print("No nRF module detected. Retrying...")
        nrf = initiate_nrf(retries=3)
        i += 1
        if i == 3:
            print('Restarting')
            machine.reset()

    while time.time() - start_time < timeout:
        try:
            signal = get_rc_command(nrf, delay=0.002)
            attempt = 0
            while signal is None and attempt < retries:
                # nrf = initiate_nrf()
                print("No initial command. Retrying...")
                signal = get_rc_command(nrf, delay=0.002)
                attempt += 1

            if to_print:
                print(f'{signal=}')
            if signal is not None:
                command = signal
                start_time = time.time()
            else:
                print("No signal received. Stopping.")
                command = [0, 50, 50]

        except (ValueError, OSError, AssertionError) as e:
            print(f"Error in controlled movement: {e}")
            command = [0, 50, 50]
            utime.sleep(0.003)  # Pause before retrying
            nrf = initiate_nrf(retries=3)
            # while nrf is None:
            if nrf is None:
                command = [0, 50, 50]
                print("No nRF module detected. Retrying...")
                # nrf = initiate_nrf(retries=500)
                machine.reset()


def motors_thread(to_print=True, timeout=300):
    time.sleep(2)
    print((('-' * 30) + '\n') * 100)
    global command
    global control_mode

    print((('=' * 30) + '\n') * 100)
    start_time = time.time()
    while time.time() - start_time < timeout:
        print(f'rolling {time.time() - start_time}')

        b, y, x = command

        if not (b == 0 and x == 50 and y == 50):
            start_time = time.time()

        print(f'Rolling for: {b=}, {y=}, {x=}')

        move(x, y, DETAILED_CONTROL)

        control_mode = arm_control(servos, control_mode, b)
        time.sleep(0.05)


def control_loop(to_print=True):
    stop()
    _thread.start_new_thread(signal_thread, ())
    motors_thread()

stop()
time.sleep(3)

if __name__ == '__main__':
    control_loop(to_print=True)



