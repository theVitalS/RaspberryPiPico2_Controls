from machine import Pin, SPI
from nrf24l01 import NRF24L01
import utime

# Pin configuration
csn = Pin(17, Pin.OUT)
ce = Pin(16, Pin.OUT)
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(20))

# Initialize nRF24L01 as a transmitter
nrf = NRF24L01(spi, csn, ce, payload_size=32)
nrf.open_tx_pipe(b'1Node')

counter = 1  # Start with 1 flash
while True:
    try:
        msg = f"{counter}"  # Send the number as a string
        print("Sending:", msg)
        nrf.send(msg.encode())
        print("Message sent!")
        counter += 1  # Increment the counter
        if counter > 5:  # Reset after 5 flashes
            counter = 1
        utime.sleep(3)  # Wait 3 seconds between messages
    except OSError:
        print("Send failed. Retrying...")
