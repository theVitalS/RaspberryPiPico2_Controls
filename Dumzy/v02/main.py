from machine import Pin, PWM
import random
import time
import utime
from car import *
from dumzy_listner import *
from arm import *
import _thread

# from HC_SR04_distance_sensor import *


# Configuration
BASE_SPEED = 60
TURNING_SLOWDOWN = 1.4
DISTANCE_THRESHOLD = 30  # cm
RANDOM_STOP_MIN = 3  # seconds
RANDOM_STOP_MAX = 6  # seconds

commands = {
    0: stop,
    1: move_forward,
    2: move_backward,
    3: turn_left,
    4: turn_right
}


def auto(n=40, random_stops=False):
    """
    Autonomous movement logic for the car with optional random stops.
    """
    for reps in range(n):
        try:
            distance = get_distance()
            if distance is None:
                print("Distance measurement failed. Stopping robot.")
                stop()
                return

            print(f"Initial Distance: {distance:.2f} cm")
            while distance > DISTANCE_THRESHOLD:
                move_forward()
                time.sleep(0.01)
                distance = get_distance(500)
                print(f"Distance: {distance:.2f} cm")

                # Handle random stops
                if random_stops and random.randint(0, 100) < 10:  # 10% chance to stop
                    print("Random stop triggered.")
                    stop()
                    time.sleep(random.uniform(RANDOM_STOP_MIN, RANDOM_STOP_MAX))
                    random_turn()

            print("Obstacle detected! Taking evasive action.")
            stop()
            time.sleep(1)

            move_backward()
            time.sleep(0.6)

            stop()
            time.sleep(1)

            random_turn()

        except Exception as e:
            print(f"Error in auto mode: {e}")
            stop()


def controlled_movement0():
    """
    Controlled movement logic using remote commands.
    """
    try:
        nrf = initiate_nrf()

        command = None
        while command is None:
            time.sleep(0.0015)
            command = get_rc_command(nrf)
        while True:
            if command is not None:
                print(f"Command received: {command}")
                if command <= 2:
                    set_speed(BASE_SPEED)
                else:
                    set_speed(BASE_SPEED / TURNING_SLOWDOWN)

                # Execute command
                commands.get(command, stop)()

                # Wait for a new command
                while True:
                    time.sleep(0.005)
                    new_command = get_rc_command(nrf)
                    if new_command is None:
                        time.sleep(0.01)
                        nrf = initiate_nrf()
                        k = 0
                        while k <= 4 and new_command is None:
                            time.sleep(0.02)
                            new_command = get_rc_command(nrf)
                            k += 1
                    if new_command != command:
                        print(f"New command: {new_command}")
                        command = new_command
                        break
            else:
                print("No command received. Stopping.")
                stop()
                while command is None:
                    time.sleep(0.01)
                    nrf = initiate_nrf()
                    command = get_rc_command(nrf)

    except (ValueError, OSError) as e:
        print(f"Error in controlled movement: {e}")
        stop()
        time.sleep(0.1)  # Pause before retrying


def controlled_movement1():
    """
    Controlled movement logic using remote commands.
    """
    control_mode = 1
    try:
        nrf = initiate_nrf()
        command = None

        while True:
            utime.sleep(0.05)
            # Wait for the initial command
            while command is None:
                command = get_rc_command(nrf)
                if command is None:
                    print("No initial command. Retrying...")
                    utime.sleep(0.05)

            command0, command1, command2 = command[0], command[1], command[2]
            # Process the received command
            print(f"Executing command: {command}")
            if command0 <= 2:
                set_speed(BASE_SPEED)
            else:
                set_speed(BASE_SPEED / TURNING_SLOWDOWN)

            trn = {0: 0, 1: 2, 2: 8, 3: 4, 4: 6}
            arm_cmd = trn[command0]
            control_mode = arm_control(servos, control_mode, arm_cmd)

            # Execute the command
            if True:

                y, x = command1, command2
                # Scale inputs
                speed_left = max(0, min(100, y + x - 50))  # Adjust to consider both x and y.
                speed_right = max(0, min(100, y - x + 50))

                # set_speeds(speed_right, speed_left)

                # Determine directions
                if speed_left > 50:
                    set_left_speed((speed_left - 50) * 2)
                    left_forward()

                else:
                    set_left_speed((50 - speed_left) * 2)
                    left_backward()

                if speed_right > 50:
                    set_right_speed((speed_right - 50) * 2)
                    right_forward()
                else:
                    set_right_speed((50 - speed_right) * 2)
                    right_backward()

                if speed_right == 50 and speed_left == 50:
                    stop()

            # else:
            #    commands.get(command0, stop)()
            # control_mode = arm_control(servos, control_mode, command1)

            # Wait for a new command or timeout
            while True:
                trn = {0: 0, 1: 2, 2: 8, 3: 4, 4: 6}
                arm_cmd = trn[command0]
                control_mode = arm_control(servos, control_mode, arm_cmd)
                utime.sleep(0.1)  # Pause before retrying
                new_command = get_rc_command(nrf, timeout=60)  # Shorter timeout for updates
                if new_command is None:
                    print("No new command. Reinitializing...")
                    stop()
                    utime.sleep(0.1)  # Pause before retrying
                    nrf = initiate_nrf()  # Reinitialize nRF module
                    break

                if new_command != command:
                    print(f"New command received: {new_command}")
                    command = new_command
                    break
                else:
                    control_mode = arm_control(servos, control_mode, command1)

    except (ValueError, OSError) as e:
        print(f"Error in controlled movement: {e}")
        stop()
        utime.sleep(0.1)  # Pause before retrying



def signal_thread(to_print=True, timeout=300, retries=2):
    time.sleep(1)
    global command
    global control_mode

    control_mode = 1
    command = [0, 50, 50]
    start_time = time.time()
    nrf = initiate_nrf(retries=500)
    while nrf is None:
        command = [0, 50, 50]
        print("No nRF module detected. Retrying...")
        nrf = initiate_nrf(retries=500)

    while time.time() - start_time < timeout:
        try:
            signal = get_rc_command(nrf, delay=0.04)
            attempt = 0
            while signal is None and attempt < retries:
                #nrf = initiate_nrf()
                print("No initial command. Retrying...")
                signal = get_rc_command(nrf, delay=0.04)
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
            utime.sleep(0.05)  # Pause before retrying
            nrf = initiate_nrf(retries=500)
            while nrf is None:
                command = [0, 50, 50]
                print("No nRF module detected. Retrying...")
                nrf = initiate_nrf(retries=500)


def motors_thread(to_print=True, timeout=300):
    time.sleep(2)
    global command
    global control_mode

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

        if False:
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
            left_vector  = y + x  # Adjust to consider both x and y.
            right_vector = y - x

            set_left_speed(left_vector*2)
            set_right_speed(right_vector*2)

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
    control_loop(to_print=False)


