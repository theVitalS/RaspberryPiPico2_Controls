from machine import Pin, PWM, ADC
import time
from servo import Servo


# Define joystick dead zone to avoid unintended movement
DEAD_ZONE = 10000  # Adjust this value if needed to ignore small joystick movements


# Define initial angles for both servos
servo0 = Servo(pin_id=0)
servo0_angle = 90  # Start at the midpoint (90 degrees)
s0_min = 0
s0_max = 180




SERVO_FREQ = 50

# Define the PWM signal range (in microseconds)
# Adjust these values if your servo behaves differently
NEUTRAL_PULSE_WIDTH = 1500  # 1.5ms -> stop
MIN_PULSE_WIDTH = 1000      # 1ms -> full speed in one direction
MAX_PULSE_WIDTH = 2000      # 2ms -> full speed in the opposite direction

# Function to set PWM pulse width in microseconds
def set_servo_pulse(servo, pulse_width_us):
    # Convert pulse width (us) to PWM duty cycle (16-bit, 65535 steps)
    duty = int((pulse_width_us / 20000) * 65535)
    servo.duty_u16(duty)

# Set up the servo on a PWM-capable pin (GP15 in this example)
#servo0 = PWM(Pin(0))
#servo0.freq(SERVO_FREQ)




servo1 = Servo(pin_id=1)
servo1_angle = 30  # Start at the midpoint (90 degrees)
s1_min = 10
s1_max = 150

servo2 = Servo(pin_id=2)
servo2_angle = 120  # Start at the midpoint (90 degrees)
s2_min = 60
s2_max = 180


servo3 = Servo(pin_id=3)
servo3_angle = 30  # Start at the midpoint (90 degrees)
s3_min = 25
s3_max = 44


    

# Initialize the ADC for X and Y axes of the joystick
x_axis = ADC(Pin(26))  # VRx connected to GP26
y_axis = ADC(Pin(27))  # VRy connected to GP27



button = Pin(22, Pin.IN, Pin.PULL_UP)
control_mode = -1
connection_is_ok = True




# Main loop to control the servos based on joystick input
while True:
    # Read the X and Y axis values from the joystick (0-65535)
    x_value = x_axis.read_u16()
    y_value = y_axis.read_u16()
    
    if (x_value < 1000 and y_value < 1000) or (x_value > 64535 and y_value > 64535):
        control_is_ok = False
    else:
        control_is_ok = True
    
    
    # Determine the direction for servo0 (X-axis)
    if x_value < (32768 - DEAD_ZONE*2) and control_mode == -1 and control_is_ok:  # Joystick pushed left
        #set_servo_pulse(servo0, MIN_PULSE_WIDTH)
        servo0.write(65)
        print('1')
    elif x_value > (32768 + DEAD_ZONE*2) and control_mode == -1 and control_is_ok:  # Joystick pushed right
        #set_servo_pulse(servo0, MAX_PULSE_WIDTH)
        servo0.write(125)
        print('2')
    else:
        #set_servo_pulse(servo0, NEUTRAL_PULSE_WIDTH)
        servo0.write(90)
        print('3')
    

    # Determine the direction for servo1 (X-axis)
    if x_value < (32768 - DEAD_ZONE) and control_mode == 1 and control_is_ok:  # Joystick pushed left
        if servo1_angle > s1_min:  # If not already at 0 degrees
            servo1_angle -= 1  # Move towards 0 degrees
    elif x_value > (32768 + DEAD_ZONE) and control_mode == 1 and control_is_ok:  # Joystick pushed right
        if servo1_angle < s1_max:  # If not already at 180 degrees
            servo1_angle += 1  # Move towards 180 degrees

    # Determine the direction for servo2 (Y-axis)
    if y_value < (32768 - DEAD_ZONE) and control_mode == 1 and control_is_ok:  # Joystick pushed up
        if servo2_angle > s2_min:  # If not already at 0 degrees
            servo2_angle -= 1  # Move towards 0 degrees
    elif y_value > (32768 + DEAD_ZONE) and control_mode == 1 and control_is_ok:  # Joystick pushed down
        if servo2_angle < s2_max:  # If not already at 180 degrees
            servo2_angle += 1  # Move towards 180 degrees
            
    
    # Determine the direction for servo3 (Y-axis)
    if y_value < (32768 - DEAD_ZONE*2) and control_mode == -1 and control_is_ok:  # Joystick pushed up
        if servo3_angle > s3_min:  # If not already at 0 degrees
            servo3_angle -= 2  # Move towards 0 degrees
    elif y_value > (32768 + DEAD_ZONE*2) and control_mode == -1 and control_is_ok:  # Joystick pushed down
        if servo3_angle < s3_max:  # If not already at 180 degrees
            servo3_angle += 2  # Move towards 180 degrees

    
    servo1.write(servo1_angle)
    servo2.write(servo2_angle)
    #servo0.write(servo0_angle)
    servo3.write(servo3_angle)
    
    if button.value()== 0:
        control_mode *= button.value()*2-1
        time.sleep(0.5)
    

    # Print the angles for debugging (optional)
    print(f"Servo 0 Angle: servo0_angle, Servo 1 Angle: {servo1_angle}, Servo 2 Angle: {servo2_angle}, Servo 3 Angle: {servo3_angle}, mode:{control_mode}, x:{x_value}, y:{y_value}, control:{control_is_ok}")

    # Small delay to smooth out the movement
    time.sleep(0.351)
