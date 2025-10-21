from machine import Pin, SPI
from nrf24l01 import NRF24L01
import time
import utime
import machine
import _thread
from utils import log_event

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
        log_event('Initiating NRF...', 'NRF', to_print=self.debug)
        nrf = None
        for attempt in range(attempts):
            time.sleep(0.1)
            try:
                nrf = NRF24L01(spi, csn, ce, payload_size=3)
                break
            except (ValueError, OSError) as e:
                log_event("NRF init failed:", 'NRF', to_print=self.debug, error=e)

        if not nrf:
            log_event("Failed to initialize nRF24L01.", 'NRF', to_print=self.debug)
            return None

        nrf.open_tx_pipe(b'1Node')
        nrf.open_rx_pipe(1, b'2Node')
        nrf.set_channel(76)
        nrf.start_listening()

        log_event('NRF ready', 'NRF', to_print=self.debug)

        return nrf

    def _listen_loop(self):
        self.nrf = self.initiate_nrf()
        i = 0
        start_time = time.time()

        while self.nrf is None:
            log_event("No nRF module detected. Retrying...", 'NRF', to_print=self.debug)
            self.command = [0, 50, 50]
            self.nrf = self.initiate_nrf()
            i += 1
            if i >= 3:
                log_event(f'No NRF after {i} attempts. Restarting system...', 'NRF', to_print=True)
                machine.reset()

        self._running = True
        last_signal = None
        while time.time() - start_time < self.timeout:
            try:
                signal = self._get_rc_command()
                if signal:
                    self.command = signal
                    start_time = time.time()
                    if self.debug and signal != last_signal:
                        print(f'Received signal: {signal}')
                        last_signal = signal
                else:
                    self.command = [0, 50, 50]
            except (ValueError, OSError, AssertionError) as e:
                log_event(f"Error in signal loop", 'NRF', to_print=self.debug, error=e)
                utime.sleep(0.003)
                self.nrf = self.initiate_nrf()
                if self.nrf is None:
                    log_event("No nRF. Restarting...", 'NRF', to_print=self.debug)
                    self.command = [0, 50, 50]
                    machine.reset()

        self._running = False

    def _get_rc_command(self, delay=0.01, max_retries=40):
        retries = 0
        while retries <= max_retries:
            utime.sleep(delay)
            if self.nrf.any():
                try:
                    data = self.nrf.recv()
                    if data and len(data) >= 3:
                        return [data[0], data[1], data[2]]
                except Exception as e:
                    log_event(f"Receive error in _get_rc_command", 'NRF', to_print=self.debug, error=e)
            else:
                retries += 1

        if self.debug:
            t = time.localtime()
            timestamp = f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
            print(f"[{timestamp}] No data. Retry {retries-1}")
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

