import time
import machine
import sys

LOG_FILE = "robot_log.txt"


def log_event(message, prefix="SYS", error=None, delims=0, to_print=False):
    """Append timestamped event to log file, HH:MM:SS.mmm format."""
    try:
        t = time.localtime()
        ms = int((time.ticks_ms() % 1000))
        timestamp = f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}.{ms:03d}"
        if error:
            delims += 1

        with open(LOG_FILE, "a") as f:
            f.write(f"{('-'*25+'\n')*delims}")
            if error:
                f.write(f"[{timestamp}] [{prefix}] Error:{str(error)}\n")
            f.write(f"[{timestamp}] [{prefix}] {message}\n")
            f.write(f"{('-'*25+'\n')*delims}")

        if to_print:
            print(f"{message}  {error}")

    except Exception as e:
        print(f"[Logging Error] {e}")

def safe_reboot(reason="Unknown reason", prefix="SYS", error=None, delay=0.5):
    """Logs reason for restart and safely reboots the board."""
    try:
        log_event(f"Rebooting system: {reason}", prefix=prefix, error=error, to_print=True)
        print(f"[Reboot] {reason}")
        time.sleep(delay)
    except Exception as e:
        print(f"[Reboot Logging Error] {e}")
    machine.reset()
