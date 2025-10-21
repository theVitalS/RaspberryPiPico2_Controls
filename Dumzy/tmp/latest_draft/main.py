from machine import time_pulse_us
import time
import _thread, gc
from dumzy_listner import start_signal_listener, get_latest_command
from arm import *
from car import MotorController
from utils import log_event, safe_reboot

motor = MotorController(detailed_control=True, debug=False)

def motors_thread(timeout=300):
    global last_chekin
    control_mode = 1
    start_time = time.time()
    last_switch = start_time

    while time.time() - start_time < timeout:
        b, y, x = get_latest_command()

        if not (b == 0 and x == 50 and y == 50):
            start_time = time.time()

        if motor.debug:
            print(f'[Main] Command received: {b=}, {y=}, {x=}')
        motor.move(x, y)
        if b != 5:
            arm_control(servos, control_mode, b)
        elif time.time() - last_switch > 1:
            control_mode *= -1
            last_switch = time.time()
            if motor.debug:
                print(f'[Main] Control mode switched: {control_mode}')

        last_chekin = time.time()
        time.sleep(0.01)


def main():
    log_event("Starting", "MAIN", delims=2)
    try:
        motor.stop()
        time.sleep(1)
        start_signal_listener()
        motors_thread()
        log_event("Robot finished run due to inactivity.", "MAIN")
    except Exception as e:
        safe_reboot("Main loop exception", prefix="MAIN", error=e)

if __name__ == '__main__':
    last_chekin = time.time()
    gc.collect()
    main()
