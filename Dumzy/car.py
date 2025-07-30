from machine import Pin, PWM

# Define the GPIO pins for motor control
rf = Pin(4, Pin.OUT)
rb = Pin(5, Pin.OUT)
lf = Pin(6, Pin.OUT)
lb = Pin(7, Pin.OUT)

ENA = PWM(Pin(3))
ENB = PWM(Pin(8))  # PWM pin for speed control (ENA)

# Set PWM Frequency
ENA.freq(1000)  # Set frequency to 1kHz
ENB.freq(1000)

# standard_speed = 50
drag_factor = 0  # -0.1 #-0.075
base_speed = 80
turning_slowdown = 2


def set_speed(speed, drag_factor=drag_factor, turn_left_factor=0):
    ENA.duty_u16(int(speed * (1 + drag_factor + turn_left_factor) * 65535 / 100))
    ENB.duty_u16(int(speed * (1 - drag_factor - turn_left_factor) * 65535 / 100))


def set_right_speed(speed, to_print=True):
    if speed < 0:
        speed *= -1
    base_speed = 80

    res = speed*base_speed/100
    if res > 100:
        res = 100

    ENA.duty_u16(int(res * 65535 / 100))
    if to_print:
        print(f'ENA duty: {int(res * 65535 / 100)}')


def set_left_speed(speed, to_print=True):
    if speed < 0:
        speed *= -1
    base_speed = 80

    res = speed * base_speed / 100
    if res > 100:
        res = 100

    ENB.duty_u16(int(res * 65535 / 100))
    if to_print:
        print(f'ENB duty: {int(res * 65535 / 100)}')


set_speed(base_speed)


def left_forward():
    lb.low()
    lf.high()


def right_forward():
    rb.low()
    rf.high()


def left_backward():
    lf.low()
    lb.high()


def right_backward():
    rf.low()
    rb.high()


def move_forward(to_print=False):
    if to_print:
        print('moving_forward')
    left_forward()
    right_forward()


def move_backward():
    left_backward()
    right_backward()


def turn_left():
    left_backward()
    right_forward()

def turn_right():
    left_forward()
    right_backward()

def stop():
    lf.low()
    lb.low()
    rf.low()
    rb.low()


def move(x, y, DETAILED_CONTROL=True):
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