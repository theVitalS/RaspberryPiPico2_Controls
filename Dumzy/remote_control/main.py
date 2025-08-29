from machine import Pin, SPI, reset
from nrf24l01 import NRF24L01
from joystick import get_joystick_signal
import utime
import time


class RemoteController:
    # ----------------------------------------------------------------
    # Configuration
    # ----------------------------------------------------------------
    TO_RESTART = True
    MAX_INIT_RETRIES = 5
    MAX_SEND_RETRIES = 10
    CHANNEL = 76
    PAYLOAD_SIZE = 8

    # Pin assignments
    PIN_CE = 20
    PIN_CSN = 17
    PIN_SCK = 18
    PIN_MOSI = 19
    PIN_MISO = 16

    INPUT_PINS = {
        0: 4,   # GP0 -> value 4
        1: 2,   # GP1 -> value 2
        2: 5,   # GP2 -> value 5
        3: 1,   # GP3 -> value 1
        4: 3    # GP4 -> value 3
    }

    def __init__(self, debug=True):
        self.debug = debug
        self.nrf = self._init_nrf()
        self.input_pins = self._init_input_pins()
        self.fail_count = 0

    # ----------------------------------------------------------------
    # Initialization
    # ----------------------------------------------------------------
    def _init_nrf(self):
        """Initialize and return an NRF24L01 instance with retries."""
        ce = Pin(self.PIN_CE, Pin.OUT, value=0)
        csn = Pin(self.PIN_CSN, Pin.OUT, value=1)

        spi = SPI(0, baudrate=5_000_000, polarity=0, phase=0,
                  sck=Pin(self.PIN_SCK), mosi=Pin(self.PIN_MOSI), miso=Pin(self.PIN_MISO))

        retries = 0
        while retries < self.MAX_INIT_RETRIES:
            try:
                nrf = NRF24L01(spi, csn, ce, payload_size=self.PAYLOAD_SIZE)
                nrf.open_tx_pipe(b'1Node')
                nrf.open_rx_pipe(1, b'2Node')
                nrf.stop_listening()
                nrf.set_channel(self.CHANNEL)
                if self.debug:
                    print("NRF24L01 initialized successfully.")
                return nrf
            except (ValueError, OSError) as e:
                print(f"NRF init failed ({retries+1}/{self.MAX_INIT_RETRIES}): {e}")
                retries += 1
                utime.sleep(0.2)

        if self.TO_RESTART:
            print("=" * 40)
            print("!!! RESETTING SYSTEM: NRF init failed !!!")
            print("=" * 40)
            reset()

        raise RuntimeError("NRF initialization failed")

    def _init_input_pins(self):
        """Return dict of Pin objects mapped to values."""
        return {Pin(pin, Pin.IN, Pin.PULL_DOWN): val for pin, val in self.INPUT_PINS.items()}

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------
    def read_input_pins(self):
        """Return mapped value from input pins, or 0 if none active."""
        for pin, val in self.input_pins.items():
            if pin.value():
                return val
        return 0

    def send_message(self, d1, d2, d3):
        """Send a compact 3-byte message."""
        data = bytes([d1, d2, d3])
        try:
            self.nrf.send(data)
            if self.debug:
                now = time.localtime()
                print(f"[{now[4]:02}:{now[5]:02}] Sent: {data}")
            return True
        except OSError as e:
            if self.debug:
                print(f"Send failed: {e}")
            return False

    # ----------------------------------------------------------------
    # Main loop
    # ----------------------------------------------------------------
    def run(self):
        """Main loop: read inputs and send messages."""
        while True:
            d1 = self.read_input_pins()
            d2, d3 = get_joystick_signal()

            if self.debug:
                print(f"Sending: {d1}, {d2}, {d3}")

            if self.send_message(d1, d2, d3):
                self.fail_count = 0  # reset on success
            else:
                self.fail_count += 1
                utime.sleep(0.1)

                if self.fail_count > self.MAX_SEND_RETRIES and self.TO_RESTART:
                    print("=" * 40)
                    print("!!! RESETTING SYSTEM: too many send failures !!!")
                    print("=" * 40)
                    reset()

            utime.sleep(0.001)


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------
if __name__ == "__main__":
    controller = RemoteController(debug=True)
    controller.run()
