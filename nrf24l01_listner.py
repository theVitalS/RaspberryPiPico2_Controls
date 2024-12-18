from machine import Pin, SPI
from nrf24l01 import NRF24L01
import utime

# Pin configuration for nRF24L01
csn = Pin(17, Pin.OUT)  # CSN -> GP17
ce = Pin(16, Pin.OUT)   # CE -> GP16
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(20))

# Built-in LED setup
led = Pin(25, Pin.OUT)  # GP25 is the built-in LED pin

# Initialize nRF24L01 as a receiver
nrf = NRF24L01(spi, csn, ce, payload_size=32)
nrf.open_rx_pipe(1, b'1Node')  # Listening on pipe address '1Node'
nrf.start_listening()

print("Listening for messages...")

# Function to flash LED a given number of times
def flash_led(times, duration=0.3):
    for _ in range(times):
        led.value(1)  # LED ON
        utime.sleep(duration)
        led.value(0)  # LED OFF
        utime.sleep(duration)

# Main loop to check for messages
while True:
    if nrf.any():  # Data available
        while nrf.any():  # Read all available messages
            msg = nrf.recv()  # Raw data received
            print("Raw received:", msg)  # Debug: print the raw data
            try:
                # Strip null bytes and decode to string
                clean_msg = msg.decode().strip('\x00').strip()
                print(f"Cleaned message: '{clean_msg}'")  # Debug cleaned message
                num_flashes = int(clean_msg)  # Convert to integer
                print(f"Flashing LED {num_flashes} times")
                flash_led(num_flashes)  # Flash LED the received number of times
            except ValueError:
                print("Invalid data received:", msg)  # Debug invalid data
    utime.sleep(0.1)  # Short delay to avoid excessive polling
