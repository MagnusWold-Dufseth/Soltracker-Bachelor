# server_start.py
import subprocess
import atexit
import signal
import sys
import time

SYSTEMCTL = "/usr/bin/systemctl"
IP = "/usr/sbin/ip"
RFKILL = "/usr/sbin/rfkill"


def _run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.stderr.strip():
        print(result.stderr.strip())

    return result.returncode


def start_ap():
    print("Starter SolarTracker AP...")

    # Fjern eventuell soft-block på wifi
    _run(["sudo", RFKILL, "unblock", "wifi"])
    _run(["sudo", RFKILL, "unblock", "all"])

    # Stopp ting som kan forstyrre AP-modus
    _run(["sudo", SYSTEMCTL, "stop", "wpa_supplicant@wlan0"])
    _run(["sudo", SYSTEMCTL, "stop", "hostapd"])
    _run(["sudo", SYSTEMCTL, "stop", "dnsmasq"])

    # Nullstill wlan0 og sett fast AP-IP
    _run(["sudo", IP, "addr", "flush", "dev", "wlan0"])
    _run(["sudo", IP, "link", "set", "wlan0", "up"])
    _run(["sudo", IP, "addr", "add", "192.168.4.1/24", "dev", "wlan0"])

    time.sleep(1.0)

    # Start DHCP først, så access point
    _run(["sudo", SYSTEMCTL, "start", "dnsmasq"])
    _run(["sudo", SYSTEMCTL, "start", "hostapd"])

    print("SolarTracker AP skal nå være oppe.")


def stop_ap():
    print("Stopper SolarTracker AP...")
    _run(["sudo", SYSTEMCTL, "stop", "hostapd"])
    _run(["sudo", SYSTEMCTL, "stop", "dnsmasq"])


def enable_ap_lifecycle():
    # Start AP med en gang programmet starter
    start_ap()

    # Stopp AP ved normal avslutning
    atexit.register(stop_ap)

    def _handle_exit(sig, frame):
        stop_ap()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle_exit)
    signal.signal(signal.SIGTERM, _handle_exit)