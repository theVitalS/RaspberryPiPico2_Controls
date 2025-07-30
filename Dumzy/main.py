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

        if x == 101 and y == 101:
            b = 5
            x = 50
            y = 50

        if not (b == 0 and x == 50 and y == 50):
            start_time = time.time()

        print(f'Rolling for: {b=}, {y=}, {x=}')

        if not DETAILED_CONTROL:
            if x < 50:
                turn_left()
            elif x > 50:
                turn_right()
            elif y > 50:
                move_forward()
            elif y < 50:
                move_backward()
            else:
                stop()
        else:
            # Scale inputs
            y -= 50
            x -= 50
            left_vector = y + x  # Adjust to consider both x and y.
            right_vector = y - x

            set_left_speed(left_vector * 2)
            set_right_speed(right_vector * 2)

            stop()
            if left_vector > 0:
                left_forward()
            if left_vector < 0:
                left_backward()
            if right_vector > 0:
                right_forward()
            if right_vector < 0:
                right_backward()

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



