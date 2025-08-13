from machine import Pin, ADC
import time


def transform_value(input):
    DEAD_ZONE = 3000

    if 32768 - DEAD_ZONE < input < 32768 + DEAD_ZONE:
        return 50
    else:
        return 50 - (input - 32768) / 32768 * 50


def get_joystick_signal(output_type='2x100'):
    # Constants
    DEAD_ZONE = 8000  # Adjust based on joystick sensitivity

    # Initialize the ADC for X and Y axes of the joystick
    x_axis = ADC(Pin(27))  # VRx connected to GP26
    y_axis = ADC(Pin(26))  # VRy connected to GP27

    button = Pin(22, Pin.IN, Pin.PULL_UP)  # Joystick button

    # Read the X and Y axis values from the joystick (0-65535)
    x_value = x_axis.read_u16()
    y_value = y_axis.read_u16()
    print(f'{x_value=} {y_value=}')

    n = 5

    """
    # Check for valid joystick connection
    if (x_value < DEAD_ZONE / n and y_value < DEAD_ZONE / n) or (
            x_value > 65535 - DEAD_ZONE / n and y_value > 65535 - DEAD_ZONE / n):

        print(f'Potential connection problem  ---  {x_value=}   {y_value=}')
        if output_type == '2x100':
            return [50, 50]
        else:
            return 0
    """
    # Handle button press
    if button.value() == 0:
        print(f'signal= 5 --- {x_value=} {y_value=}')
        if output_type == '2x100':
            return [101, 101]
        else:
            return 5

    # Calculate directions
    x = 0
    y = 0

    if output_type == '2x100':
        x = transform_value(x_value)
        y = transform_value(y_value)

        return [int(y), int(x)]

    else:
        if x_value < (32768 - DEAD_ZONE):  # Joystick pushed left
            x = 1
        elif x_value > (32768 + DEAD_ZONE):  # Joystick pushed right
            x = -1

        if y_value < (32768 - DEAD_ZONE):  # Joystick pushed up
            y = -1
        elif y_value > (32768 + DEAD_ZONE):  # Joystick pushed down
            y = 1

        # Calculate signal
        if x == 0 and y == 0:
            signal = 0
        else:
            signal = y * 3 + 5 + x

        # Print for debugging
        # print(f"{x_value=}, {x=}, {y_value=}, {y=}, {signal=}")
        return signal


def check_joystick_signal():
    while True:
        joystick_signal = get_joystick_signal()
        print(f'{joystick_signal=}')
        print('-' * 50)
        time.sleep(0.1)  # Debounce

# check_joystick_signal()
