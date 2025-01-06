from machine import Pin, PWM
import random
import time
from car import *
from HC_SR04_distance_sensor import *
from dumzy_listner import *

stop()
time.sleep(2)


def auto(n=40, random_stops=False):
    reps = 0
    while reps < n:

        distance = get_distance()
        if not distance:
            print("Distance measurement failed. Stopping robot.")
            stop()
            return
        print("Distance: {:.2f} cm".format(distance))

        start_time = time.time()

        while distance > 30:
            move_forward()
            time.sleep(0.01)

            distance = get_distance(500)
            print("Distance: {:.2f} cm".format(distance))

            if random_stops:
                current_time = time.time()
                t = current_time - start_time
                if t <= random.randint(3, 6):
                    print('Go random turn')
                    random_turn()

        stop()
        time.sleep(1)

        move_backward()
        time.sleep(0.6)

        stop()
        time.sleep(1)

        random_turn()

        reps += 1


def controled_movement():
    while True:
        command = int(get_rc_command())
        if command == 1:
            move_forward()
        elif command == 2:
            move_backward()
        elif command == 3:
            turn_left(n=0.05)
        elif command == 4:
            turn_right(n=0.05)
        else:
            stop()
        time.sleep(0.001)


# auto()
controled_movement()

