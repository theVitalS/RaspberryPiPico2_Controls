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

# Output pins for controlling voltage
output_pins = [
    Pin(2, Pin.OUT),  # GP2
    Pin(3, Pin.OUT),  # GP3
    Pin(4, Pin.OUT),  # GP4
    Pin(5, Pin.OUT),  # GP5
]


def set_output_pin(index):
    """Set the specified output pin HIGH, and all others LOW."""
    for i, pin in enumerate(output_pins):
        pin.value(1 if i == index else 0)  # Set only the specified pin HIGH


def get_signal(to_print=False):
    while True:
        if nrf.any():  # Check if data is available
            try:
                msg = nrf.recv()  # Receive the message
                if to_print:
                    print("Received raw message:", msg)

                # Decode and strip null bytes
                message = msg.decode().strip('\x00')
                if not message:  # Ignore empty messages
                    if to_print:
                        print("Empty or invalid message received!")
                    return -1

                signal = int(message)  # Convert to integer
                if to_print:
                    print(f"Received signal: {signal}")

                return signal
            except (ValueError, OSError) as e:
                if to_print:
                    print("Invalid message or error:", e)
        else:
            #print('waiting')
            utime.sleep(0.01)  # Short delay to avoid excessive polling


start = utime.ticks_ms()  # Time message is received
print(get_signal())
end = utime.ticks_ms()  # Time message is received
print(f'Time diff: {utime.ticks_diff(end, start)}')


while True:
    start = utime.ticks_ms()  # Time message is received
    get_signal()
    end = utime.ticks_ms()  # Time message is received
    print(f'Time diff: {utime.ticks_diff(end, start)}')

