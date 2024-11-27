from machine import Pin, PWM
import time

# Define the GPIO pins for motor control
lf = Pin(13, Pin.OUT)
lb = Pin(12, Pin.OUT)
rf = Pin(11, Pin.OUT)
rb = Pin(10, Pin.OUT)


# Optional: PWM for speed control, replace Pin(X) with your PWM pin if needed
# pwm_a = PWM(Pin(X))  # Replace X with the pin connected to ENA (e.g., GPIO 10)
# pwm_b = PWM(Pin(X))  # Replace X with the pin connected to ENB (e.g., GPIO 11)
# pwm_a.freq(1000)     # Set frequency for PWM
# pwm_b.freq(1000)

def left_forward():
    # print('left_forward')
    lb.low()
    lf.high()


def right_forward():
    # print('right_forward')
    rb.low()
    rf.high()


def left_backward():
    # print('left_backward')
    lf.low()
    lb.high()


def right_backward():
    # print('right_backward')
    rf.low()
    rb.high()


def move_forward():
    left_forward()
    right_forward()


def move_backward():
    left_backward()
    right_backward()


def turn_left(n=1.5):
    left_backward()
    right_forward()
    time.sleep(n)
    stop()


def turn_right(n=1.5):
    left_forward()
    right_backward()
    time.sleep(n)
    stop()


def stop():
    lf.low()
    lb.low()
    rf.low()
    rb.low()


def test1():
    stop()
    time.sleep(0.5)
    move_forward()
    time.sleep(1)
    stop()
    time.sleep(1)
    move_backward()
    time.sleep(1)
    stop()
    turn_left()
    time.sleep(1)
    turn_right()
    time.sleep(1)
    move_forward()
    time.sleep(1)
    stop()
    time.sleep(1)
    move_backward()
    time.sleep(1)
    stop()


def test2():
    stop()
    time.sleep(0.5)
    move_forward()
    time.sleep(1)
    stop()
    time.sleep(1)
    move_backward()
    time.sleep(1)
    stop()
    turn_left()
    time.sleep(1)
    turn_right()
    stop()


def test3(x=8):
    i = 0
    while i < x:
        move_forward()
        time.sleep(1)
        stop()
        time.sleep(2)

        # Example: Turn left for 1 second, then stop
        move_backward()
        time.sleep(1)
        stop()
        time.sleep(1)
        i += 1
