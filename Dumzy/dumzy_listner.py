from machine import Pin, SPI
from nrf24l01 import NRF24L01
import time
import utime

#  nRF24L01 setup for sender
ce = Pin(9, Pin.OUT)  # CE -> GP13
csn = Pin(13, Pin.OUT)  # CSN -> GP14

spi = SPI(1, #baudrate=5000000, polarity=0, phase=0,
          sck=Pin(10), mosi=Pin(11), miso=Pin(12))

# Set CE and CSN to their default states
ce.value(0)
csn.value(1)


def initiate_nrf(to_print=False, retries=50):
    # Initialize nRF24L01
    if to_print:
        print('-' * 40)
        print('Initiating NRF')
    nrf = None
    attempt = 0
    while not nrf and attempt < retries:
        time.sleep(0.1)
        try:
            nrf = NRF24L01(spi, csn, ce, payload_size=8)  # Use default payload size
        except (ValueError, OSError) as e:
            attempt += 1
            print("Failed to init:", e)

    if not nrf:
        print("Failed to initialize nRF24L01.")
        return None
    nrf.open_tx_pipe(b'1Node')  # Transmitter address
    nrf.open_rx_pipe(1, b'2Node')  # Receiver address
    nrf.set_channel(76)  # Set RF communication channel
    nrf.start_listening()  # Start listening for messages

    if to_print:
        print('NRF initiated')
        print('-' * 40)

    return nrf


def get_rc_command099(nrf):
    k = 0
    # print('Getting command')
    while True:
        # print('listening...')
        if nrf.any():  # Check if data is available
            try:
                # print(f'{k=}')
                k = 0

                data = nrf.recv()  # Expecting a 2-byte payload
                d1, d2 = data[0], data[1]
                '''
                msg = nrf.recv()  # Receive the message
                #print("Received raw message:", msg)

                # Decode and strip null bytes
                message = msg.decode().strip('\x00')
                if not message:  # Ignore empty messages
                    #print("Empty or invalid message received!")
                    raise ValueError("ValueError   ---    Empty or invalid message received!")
                    #continue
                '''
                signal = d1  # int(message[0])  # Convert to integer
                print(f"Received signal: {signal}")

                if 0 <= signal <= 99:
                    print(f'{signal=}')
                    return signal
                else:
                    print("Invalid signal received, ignoring.")

            except (ValueError, OSError) as e:
                print("Invalid message or error:", e)
        else:
            k += 1
            if k == 90:
                print('command - none')
                return None

        #    print('...')

        # utime.sleep(0.001)  # Short delay to avoid excessive polling


def get_rc_command(nrf, timeout=40, to_print=True, delay=0.01):
    """
    Wait for a remote control command from the nRF module.
    Returns the received signal or None if no signal is received within the timeout.
    """
    retries = 0
    while retries < timeout:
        utime.sleep(delay)  # Small delay to avoid tight polling
        if nrf.any():  # Check if data is available
            try:
                data = None
                data = nrf.recv()  # Expecting a 3-byte payload
                d1, d2, d3 = data[0], data[1], data[2]
                signal = data
                if to_print:
                    print(f"Received signal: {signal}, {d1=} {d2=}, {d3=}")

                if signal:
                    return [d1, d2, d3]
                else:
                    print("Invalid signal received, ignoring.")
            except (ValueError, OSError) as e:
                print(f"Error receiving message: {e}")
        else:
            retries += 1
            print('Unsuccessful attempt:', retries)

    print("Command timeout: No signal received.")
    return None


def check_signal():
    while True:
        time.sleep(0.2)
        nrf = initiate_nrf()
        print(get_rc_command(nrf))

# check_signal()



