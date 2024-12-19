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

def send_flashes(number):
    """Send the number of flashes to the receiver."""
    message = f"{number}"  # Convert number to string
    try:
        print(f"Sending: {message}")
        nrf.send(message.encode())  # Encode and send the message
        print("Message sent successfully!")
    except OSError:
        print("Failed to send message!")

while True:
    for flashes in range(1, 6):  # Loop to send 1 to 5 flashes
        send_flashes(flashes)
        utime.sleep(2)  # Wait 5 seconds before sending the next message

