from machine import Pin, time_pulse_us
import time

# Pin definitions
TRIG_PIN = 19  # Change to the GPIO pin connected to Trig
ECHO_PIN = 18  # Change to the GPIO pin connected to Echo

# Set up pins
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)


# Function to measure distance
def measure_distance():
    # Ensure the trigger pin is low initially
    trig.low()
    time.sleep_us(10)

    # Send a 10µs pulse to trigger the measurement
    trig.high()
    time.sleep_us(10)
    trig.low()

    # Measure the duration of the echo pulse
    duration = time_pulse_us(echo, 1, 30000)  # Wait up to 30ms for echo high

    # Check for timeout
    if duration == -1:
        print("Timeout - No echo received")
        return None

    # Calculate distance in centimeters
    distance = (duration * 0.0343) / 2  # speed of sound: 343m/s -> 0.0343 cm/µs
    return distance


def get_distance(retries=float('inf'), to_print=True):
    if to_print: print('Start Measuring distance')
    for _ in range(retries):
        if to_print: print(f'Measuring distance, attempt: {_}')
        distance = measure_distance()
        if distance and distance > 0:
            return distance
    return None


def hc_sr04_example_usage():
    # Main loop
    while True:
        distance = measure_distance()
        if distance is not None:
            print("Distance: {:.2f} cm".format(distance))
        else:
            print("Distance measurement failed")
        time.sleep(1)  # Delay between measurements

# hc_sr04_example_usage()

