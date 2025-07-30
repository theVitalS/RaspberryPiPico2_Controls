from machine import Pin, PWM, ADC
import time
from dumzy_listner import *

# Define joystick dead zone to avoid unintended movement
DEAD_ZONE = 10000  # Adjust this value if needed to ignore small joystick movements
SERVO_FREQ = 50

# Define the PWM signal range (in microseconds)
# Adjust these values if your servo behaves differently
NEUTRAL_PULSE_WIDTH = 1500  # 1.5ms -> stop
MIN_PULSE_WIDTH = 1000  # 1ms -> full speed in one direction
MAX_PULSE_WIDTH = 2000  # 2ms -> full speed in the opposite direction


class Servo:
    def __init__(self, pin_id, min_angle=0, max_angle=180, current_angle=90, rolling=False):
        self.servo = PWM(Pin(pin_id))
        self.servo.freq(SERVO_FREQ)
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.current_angle = current_angle
        self.rolling = rolling

        self.servo.duty_u16(int((self.current_angle / 180.0 * 2.0 + 0.5) / 20.0 * 65535.0))

    def set_angle(self, angle):
        # Angle should be between 0 and 180 degrees
        if self.min_angle <= angle <= self.max_angle:
            self.current_angle = angle
            self.servo.duty_u16(int((angle / 180.0 * 2.0 + 0.5) / 20.0 * 65535.0))

    def move(self, delta_angle):
        if not self.rolling:
            # Calculate new angle
            new_angle = self.current_angle + delta_angle
            # Ensure the new angle is within the limits
            new_angle = max(self.min_angle, min(self.max_angle, new_angle))
            # Set the new angle
            self.set_angle(new_angle)
        else:
            if delta_angle > 0:
                self.set_angle(self.max_angle)
            if delta_angle < 0:
                self.set_angle(self.min_angle)
            time.sleep(0.005)
            self.set_angle(self.current_angle)


servo0 = Servo(pin_id=16, min_angle=0, max_angle=180, current_angle=90, )
servo1 = Servo(pin_id=17, min_angle=10, max_angle=150, current_angle=0)
servo2 = Servo(pin_id=18, min_angle=60, max_angle=180, current_angle=120)
servo3 = Servo(pin_id=19, min_angle=25, max_angle=44, current_angle=30)


servos = [servo0, servo1, servo2, servo3]


def arm_control(servos, control_mode, signal):
    if signal == 5:
        control_mode *= -1
        return control_mode

    # dirs = {1: [-1, -1], 2: [0, -1], 3: [1, -1], 4: [-1, 0], 6: [1, 0], 7: [-1, 1], 8: [0, 1], 9: [1, 1], None: [0, 0], 0: [0, 0]}
    dirs = {None: [0, 0], 0: [0, 0], 1: [1, 0], 2: [-1, 0], 3: [0, -1], 4: [0, 1]}

    a = 3

    if signal and 0 <= signal <= 9:
        y, x= dirs[signal]
    else:
        x, y = 0, 0

    if control_mode == 1:
        servos[1].move(x * a)
        servos[2].move(y * a)
    elif control_mode == -1:
        servos[0].move(x * a)
        servos[3].move(y * a)

    return control_mode


def check_arm():
    nrf = initiate_nrf()
    control_mode = -1
    while True:
        try:
            signal = get_rc_command(nrf)
        except (ValueError, OSError) as e:
            print(f"{str(time.timestemp())}: Invalid message or error {e}")
            nrf = initiate_nrf()
            signal = 0
        control_mode = arm_control(servos, control_mode, signal)
        time.sleep(0.001)




