from machine import Pin, SPI
from nrf24l01 import NRF24L01
import utime

#  nRF24L01 setup for sender
ce = Pin(11, Pin.OUT)  # CE -> GP13
csn = Pin(10, Pin.OUT)  # CSN -> GP14

spi = SPI(1, baudrate=5000000, polarity=0, phase=0,
          sck=Pin(14), mosi=Pin(15), miso=Pin(12))

# Set CE and CSN to their default states
ce.value(0)
csn.value(1)


def initiate_nrf():
    # Initialize nRF24L01
    print('Initiating NRF')
    nrf = None
    while not nrf:
        try:
            nrf = NRF24L01(spi, csn, ce, payload_size=8)  # Use default payload size
        except (ValueError, OSError) as e:
            print("Failed to init:", e)

    nrf.open_tx_pipe(b'1Node')  # Transmitter address
    nrf.open_rx_pipe(1, b'2Node')  # Receiver address
    nrf.set_channel(76)  # Set RF communication channel
    nrf.start_listening()  # Start listening for messages
    print('NRF initiated')
    print('-' * 40)

    return nrf


def get_rc_command(nrf):
    k = 0
    # print('Getting command')
    while True:
        # print('listening...')
        if nrf.any():  # Check if data is available
            try:
                # print(f'{k=}')
                k = 0
                msg = nrf.recv()  # Receive the message
                # print("Received raw message:", msg)

                # Decode and strip null bytes
                message = msg.decode().strip('\x00')
                if not message:  # Ignore empty messages
                    # print("Empty or invalid message received!")
                    raise ValueError("ValueError   ---    Empty or invalid message received!")
                    # continue

                signal = int(message)  # Convert to integer
                # print(f"Received signal: {signal}")

                if 0 <= signal <= 4:
                    return signal
                else:
                    print("Invalid signal received, ignoring.")

            except (ValueError, OSError) as e:
                print("Invalid message or error:", e)
        else:
            k += 1
            if k == 150:
                return None
        #    print('...')

        utime.sleep(0.001)  # Short delay to avoid excessive polling





