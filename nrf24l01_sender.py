from machine import Pin, SPI
from nrf24l01 import NRF24L01
import utime

# nRF24L01 setup
csn = Pin(17, Pin.OUT)  # CSN -> GP17
ce = Pin(16, Pin.OUT)   # CE -> GP16
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(20))

# Initialize nRF24L01
nrf = NRF24L01(spi, csn, ce, payload_size=32)  # Use default payload size
nrf.open_tx_pipe(b'1Node')                    # Transmitter address
nrf.open_rx_pipe(1, b'2Node')                 # Receiver address
nrf.stop_listening()                          # Ensure it's in TX mode
nrf.set_channel(76)                           # Set RF communication channel

# Input pins for reading voltages
input_pins = [
    Pin(2, Pin.IN, Pin.PULL_DOWN),  # GP2
    Pin(3, Pin.IN, Pin.PULL_DOWN),  # GP3
    Pin(4, Pin.IN, Pin.PULL_DOWN),  # GP4
    Pin(5, Pin.IN, Pin.PULL_DOWN),  # GP5
]

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
        success = nrf.send(message.encode())  # Encode and send the message
        if success:
            print("Message sent successfully!")
        else:
            print("Message failed to send!")
    except OSError as e:
        print(f"Send failed! Error: {e}")

while True:
    number_to_send = read_input_pins()  # Determine the number to send
    send_message(str(number_to_send))  # Convert to string and send
    utime.sleep(0.5)  # Send messages every 500ms
