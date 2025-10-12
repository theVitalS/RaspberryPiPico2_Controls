from machine import Pin, SPI
from nrf24l01 import NRF24L01
import time
import utime
import machine
import _thread
import sys
import os
from utils import log_event, safe_reboot

# ------------------ NRF Setup ------------------

ce = Pin(9, Pin.OUT)
csn = Pin(13, Pin.OUT)
spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(12))

ce.value(0)
csn.value(1)

# ------------------ Signal Receiver ------------------

class SignalReceiver:
    def __init__(self, timeout=600, retries=3, debug=False):
        self.timeout = timeout
        self.retries = retries
        self.debug = debug
        self.nrf = None
        self.command = [0, 50, 50]
        self._running = False

    def initiate_nrf(self, attempts=50):
        self.nrf = None
        for attempt in range(attempts):
            try:
                self.nrf = NRF24L01(spi, csn, ce, payload_size=8)
                break
            except (ValueError, OSError) as e:
                log_event(f"NRF init attempt {attempt+1} failed", "NRF", error=e, to_print=self.debug)
            utime.sleep(0.01)

        if not self.nrf:
            safe_reboot(f"Failed to initialize nRF24L01 after {attempts} attempts.", "NRF")

        try:
            self.nrf.open_tx_pipe(b'1Node')
            self.nrf.open_rx_pipe(1, b'2Node')
            self.nrf.set_channel(76)
            self.nrf.start_listening()
            log_event("NRF module initialized and listening.", "NRF")
        except Exception as e:
            safe_reboot(f"Error configuring NRF", "NRF", error=e)



    def _listen_loop(self):
        """Continuously listens for radio commands with exception safety."""
        try:
            start_time = time.time()

            self._running = True
            log_event("NRF listening loop started.", "NRF")

            while time.time() - start_time < self.timeout:
                try:
                    signal = self._get_rc_command()
                    if signal:
                        self.command = signal
                        start_time = time.time()
                    else:
                        if self.debug:
                            print("No valid signal received. Using default.")
                        self.command = [0, 50, 50]
                except (ValueError, OSError, AssertionError) as e:
                    log_event(f"Error in signal loop: {e}", "NRF", to_print=True)
                    utime.sleep(0.01)
                    self.initiate_nrf()


            log_event("NRF listener loop ended (timeout).", "NRF", to_print=self.debug)
            self._running = False

        except Exception as e:
            safe_reboot("Fatal error in _listen_loop", prefix="NRF", error=e)

    def _get_rc_command(self, delay=0.01, max_retries=50):
        retries = 0
        while retries < max_retries:
            utime.sleep(delay)
            if self.nrf.any():
                try:
                    data = self.nrf.recv()
                    if self.debug:
                        print(f"Received: {data}")
                    if len(data) >= 3:  #data and len(data) >= 3:
                        return [data[0], data[1], data[2]]
                except Exception as e:
                    log_event(f"Receive error: {e}", "NRF", to_print=True)
            else:
                retries += 1
        log_event(f"No data received after {max_retries} retries.", "NRF", to_print=self.debug)
        return None

    def get_command(self):
        return self.command

    def start(self):
        log_event("NRF listener thread starting.", "NRF")
        try:
            self.initiate_nrf()
            _thread.start_new_thread(self._listen_loop, ())
        except Exception as e:
            safe_reboot("Failed to start NRF listener thread", prefix="NRF", error=e)
        log_event("NRF listener thread started.", "NRF")


signal_receiver = SignalReceiver(debug=True)

def start_signal_listener():
    log_event("Starting signal listener...", "NRF", delims=1, to_print=True)
    signal_receiver.start()

def get_latest_command():
    return signal_receiver.get_command()

