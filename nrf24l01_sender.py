from machine import Pin, SPI
from nrf24l01 import NRF24L01
import utime

# nRF24L01 setup for sender
ce = Pin(16, Pin.OUT)   # CE -> GP13
csn = Pin(17, Pin.OUT)  # CSN -> GP14

spi = SPI(1, baudrate=5000000, polarity=0, phase=0,
          sck=Pin(14), mosi=Pin(15), miso=Pin(12))

# Set CE and CSN to their default states
ce.value(0)
csn.value(1)

# Initialize nRF24L01
nrf = None
while not nrf:
    try:
        nrf = NRF24L01(spi, csn, ce, payload_size=8)  # Use default payload size
    except (ValueError, OSError) as e:
            print("Failed to init:", e)


nrf.open_tx_pipe(b'1Node')                    # Transmitter address
nrf.open_rx_pipe(1, b'2Node')                 # Receiver address
nrf.stop_listening()                          # Ensure it's in TX mode
nrf.set_channel(76)                           # Set RF communication channel


# Input pins for reading voltages
p1 = Pin(2, Pin.IN, Pin.PULL_DOWN) # GP2
p2 = Pin(3, Pin.IN, Pin.PULL_DOWN) # GP3
p3 = Pin(4, Pin.IN, Pin.PULL_DOWN) # GP4
p4 = Pin(5, Pin.IN, Pin.PULL_DOWN) # GP5

input_pins = [p1, p2, p3, p4]

def read_input_pins():
    """Read input pins and return a number based on their states."""
    for i, pin in enumerate(input_pins, start=1):  # Check pins 1 to 4
        if pin.value():  # If HIGH (voltage detected)
            return i
    return 0  # Default to 0 if no pins are HIGH

def send_message(message):
    """Send a message to the receiver."""
    try:
        print(f"Sending: {message}")
        nrf.send(message.encode())
    except OSError as e:
        print(f"Send failed! Error: {e}")

while True:
    number_to_send = read_input_pins()  # Determine the number to send
    send_message(str(number_to_send))  # Convert to string and send
    utime.sleep(0.001)  # Send messages every 500ms

