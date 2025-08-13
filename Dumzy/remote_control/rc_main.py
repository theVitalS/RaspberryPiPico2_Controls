from machine import Pin, SPI
from nrf24l01 import NRF24L01
from joystick import get_joystick_signal
import utime
import time
import machine

"""
# nRF24L01 first setup for sender
ce = Pin(7, Pin.OUT)   # CE -> GP13
csn = Pin(6, Pin.OUT)  # CSN -> GP14

spi = SPI(1, baudrate=5000000, polarity=0, phase=0, 
          sck=Pin(14), mosi=Pin(15), miso=Pin(12))

"""

to_restart = True

ce = Pin(20, Pin.OUT)  # CE -> GP13
csn = Pin(17, Pin.OUT)  # CSN -> GP14

spi = SPI(0, baudrate=5000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))

# Set CE and CSN to their default states
ce.value(0)
csn.value(1)

# Initialize nRF24L01
nrf = None
i = 0
while not nrf:
    try:
        nrf = NRF24L01(spi, csn, ce, payload_size=8)  # Use default payload size
    except (ValueError, OSError) as e:
        print("Failed to init:", e)
        i += 1
        if i == 5 and to_restart:
            print('=' * 40)
            print('=' * 40)
            print('*****************RESET******************************')
            print('=' * 40)
            print('=' * 40)
            machine.reset()

nrf.open_tx_pipe(b'1Node')  # Transmitter address
nrf.open_rx_pipe(1, b'2Node')  # Receiver address
nrf.stop_listening()  # Ensure it's in TX mode
nrf.set_channel(76)  # Set RF communication channel

# Input pins for reading voltages
p0 = Pin(0, Pin.IN, Pin.PULL_DOWN)  # GP2
p1 = Pin(1, Pin.IN, Pin.PULL_DOWN)  # GP2
p2 = Pin(2, Pin.IN, Pin.PULL_DOWN)  # GP3
p3 = Pin(3, Pin.IN, Pin.PULL_DOWN)  # GP4
p4 = Pin(4, Pin.IN, Pin.PULL_DOWN)  # GP5

input_pins = {p0: 4, p1: 2, p2: 5, p3: 1, p4: 3}


def read_input_pins():
    """Read input pins and return a number based on their states."""
    for pin, val in input_pins.items():  # Check pins 1 to 4
        if pin.value():  # If HIGH (voltage detected)
            return val
    return 0  # Default to 0 if no pins are HIGH


def send_message0(message):
    """Send a message to the receiver."""
    try:
        print(f"Sending: {message}")
        nrf.send(message.encode())
    except OSError as e:
        print(f"Send failed! Error: {e}")


while False:
    d1 = 0
    d1 = read_input_pins()  # Determine the number to send
    d2 = 0
    d2 = get_joystick_signal()
    signal = str(d1) + str(d2)
    # print(f'{signal=}  {d1=}  {d2=}')
    send_message(signal)  # Convert to string and send
    utime.sleep(0.01)  # Send messages every 500ms


def send_message(d1, d2, d3):
    """Send a compact binary message to the receiver."""
    try:
        data = bytes([d1, d2, d3])  # Send as a 2-byte payload
        nrf.send(data)
        current_time = time.localtime()
        print(f"{current_time[4]} {current_time[5]} Sent: {data}")
    except OSError as e:
        print(f"Send failed: {e}")
        raise e


at = 0

while True:

    d1 = read_input_pins()
    d2, d3 = get_joystick_signal()
    print(f"sending: {d1}, {d2} {d3}")

    try:
        send_message(d1, d2, d3)
    except OSError as e:
        print(f'!!!!!!!!!!!!!!!!!!We are catching it  - {at=}  -  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        at += 1
        utime.sleep(0.1)
        if at > 10 and to_restart:
            print('=' * 40)
            print('=' * 40)
            print('*****************RESET******************************')
            print('=' * 40)
            print('=' * 40)
            machine.reset()


    utime.sleep(0.001)  # Shorter delay

while False:
    print(read_input_pins())
    utime.sleep(0.5)

