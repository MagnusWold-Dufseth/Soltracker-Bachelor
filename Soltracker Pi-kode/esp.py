import serial


_ser = serial.Serial(
    port="/dev/ttyAMA3",
    baudrate=115200,
    timeout=0.05,
    write_timeout=0.2,
)

def to_esp(dev_az: float, dev_alt: float, tracking_enabled: bool):
    message = (
        f"track:{int(tracking_enabled)},"
        f"az:{dev_az:.6f},"
        f"alt:{dev_alt:.6f}\n"
    )
    _ser.write(message.encode("utf-8"))


def from_esp():
    if _ser.in_waiting <= 0:
        return None 
    data = _ser.readline()
    if not data:
        return None
    if not data.endswith(b"\n"):
        return None
    return data.decode("utf-8", errors="replace").strip()
