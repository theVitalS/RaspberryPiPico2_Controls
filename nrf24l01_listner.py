from machine import Pin, SPI
from nrf24l01 import NRF24L01
import utime

# nRF24L01 setup for sender
ce = Pin(16, Pin.OUT)  # CE -> GP13
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


nrf.set_channel(76)  # Set RF communication channel
nrf.start_listening()  # Start listening for messages

p0 = Pin(2, Pin.OUT)  # GP2
p1 = Pin(3, Pin.OUT)  # GP3
p2 = Pin(4, Pin.OUT)  # GP4
p3 = Pin(5, Pin.OUT)  # GP5

# Output pins for controlling voltage
output_pins = [p0, p1, p2, p3]


def set_output_pin(index):
    """Set the specified output pin HIGH, and all others LOW."""
    for i, pin in enumerate(output_pins):
        pin.value(1 if i == index else 0)  # Set only the specified pin HIGH


i = 1
while True:

    if nrf.any():  # Check if data is available
        try:
            msg = nrf.recv()  # Receive the message
            print("Received raw message:", msg)

            # Decode and strip null bytes
            message = msg.decode().strip('\x00')
            if not message:  # Ignore empty messages
                print("Empty or invalid message received!")
                continue

            signal = int(message)  # Convert to integer
            print(f"Received signal: {signal}")

            if 0 <= signal <= 4:
                set_output_pin(signal - 1 if signal > 0 else -1)  # Map 0 to LOW for all
            else:
                print("Invalid signal received, ignoring.")

        except (ValueError, OSError) as e:
            print("Invalid message or error:", e)

    utime.sleep(0.001)  # Short delay to avoid excessive polling




