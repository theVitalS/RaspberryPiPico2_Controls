from machine import Pin, SPI
from nrf24l01 import NRF24L01
import utime

# nRF24L01 setup
csn = Pin(17, Pin.OUT)  # CSN -> GP17
ce = Pin(16, Pin.OUT)  # CE -> GP16
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(20))

# Initialize nRF24L01
nrf = NRF24L01(spi, csn, ce, payload_size=32)  # Use default payload size
nrf.open_tx_pipe(b'2Node')  # Transmitter address
nrf.open_rx_pipe(1, b'1Node')  # Receiver address
nrf.set_channel(76)  # Set RF communication channel
nrf.start_listening()  # Start listening for messages

# Initialize the onboard LED (GP25 on Raspberry Pi Pico)
led = Pin(25, Pin.OUT)


def flash_led(times):
    """Flash the onboard LED the given number of times."""
    print(f"Flashing LED {times} times")
    for _ in range(times):
        led.value(1)  # Turn LED ON
        utime.sleep(0.03)
        led.value(0)  # Turn LED OFF
        utime.sleep(0.03)


print('start')
while True:
    if nrf.any():  # Check if data is available
        try:
            msg = nrf.recv()  # Receive the message
            # print("Received raw message:", msg)

            # Decode and strip null bytes
            message = msg.decode().strip('\x00')
            if not message:  # Ignore empty messages
                print("Empty or invalid message received!")
                continue

            flashes = int(message)  # Convert to integer

            flash_led(flashes)  # Flash the LED
        except (ValueError, OSError) as e:
            print("Invalid message or error:", e)
    utime.sleep(0.01)  # Short delay to avoid excessive polling

