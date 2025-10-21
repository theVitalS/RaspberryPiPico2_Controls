from machine import Pin, SPI
from nrf24l01 import NRF24L01
import time
import utime
import machine
import _thread

# SPI and NRF24L01 setup
ce = Pin(9, Pin.OUT)  # CE -> GP13
csn = Pin(13, Pin.OUT)  # CSN -> GP14

spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(12))

ce.value(0)
csn.value(1)

class SignalReceiver:
    def __init__(self, timeout=600, retries=3, debug=False):
        self.timeout = timeout
        self.retries = retries
        self.debug = debug
        self.nrf = None
        self.command = [0, 50, 50]
        self.control_mode = 1
        self._running = False

    def initiate_nrf(self, attempts=50):
        if self.debug:
            print('-' * 40)
            print('Initiating NRF...')
        nrf = None
        for attempt in range(attempts):
            time.sleep(0.1)
            try:
                nrf = NRF24L01(spi, csn, ce, payload_size=3)
                break
            except (ValueError, OSError) as e:
                if self.debug:
                    print("NRF init failed:", e)

        if not nrf:
            print("Failed to initialize nRF24L01.")
            return None

        nrf.open_tx_pipe(b'1Node')
        nrf.open_rx_pipe(1, b'2Node')
        nrf.set_channel(76)
        nrf.start_listening()

        if self.debug:
            print('NRF ready')
            print('-' * 40)

        return nrf

    def _listen_loop(self):
        self.nrf = self.initiate_nrf()
        i = 0
        start_time = time.time()

        while self.nrf is None:
            print("No nRF module detected. Retrying...")
            self.command = [0, 50, 50]
            self.nrf = self.initiate_nrf()
            i += 1
            if i >= 3:
                print('Restarting system...')
                machine.reset()

        self._running = True
        while time.time() - start_time < self.timeout:
            try:
                signal = self._get_rc_command()
                if signal:
                    self.command = signal
                    start_time = time.time()
                else:
                    print("No valid signal received. Using default.")
                    self.command = [0, 50, 50]
            except (ValueError, OSError, AssertionError) as e:
                print(f"Error in signal loop: {e}")
                utime.sleep(0.003)
                self.nrf = self.initiate_nrf()
                if self.nrf is None:
                    print("No nRF. Restarting...")
                    self.command = [0, 50, 50]
                    machine.reset()

        self._running = False

    def _get_rc_command(self, delay=0.01, max_retries=40):
        retries = 0
        while retries < max_retries:
            utime.sleep(delay)
            if self.nrf.any():
                try:
                    data = self.nrf.recv()
                    if self.debug:
                        print(f"Received: {data}")
                    if data and len(data) >= 3:
                        return [data[0], data[1], data[2]]
                except Exception as e:
                    print(f"Receive error: {e}")
            else:
                retries += 1
                if self.debug:
                    print(f"No data. Retry {retries}")
        return None

    def get_command(self):
        return self.command

    def start(self):
        time.sleep(2)
        _thread.start_new_thread(self._listen_loop, ())

# Global instance
signal_receiver = SignalReceiver(debug=True)

def start_signal_listener():
    signal_receiver.start()

def get_latest_command():
    return signal_receiver.get_command()

def get_control_mode():
    return signal_receiver.control_mode

