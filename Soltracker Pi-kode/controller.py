# controller.py
from __future__ import annotations
import threading
from collections import deque
from datetime import datetime

_state_lock = threading.Lock()
_log_lock = threading.Lock()

state = {
    "target_az": "",
    "target_alt": "",
    "offset_az": "0",
    "offset_alt": "0",
    "tracking_enabled": False,

    "manual_az": "stop",
    "manual_alt": "stop",

    "current_az": "",
    "current_alt": "",
}

log_buffer = deque(maxlen=200)

def set_targets(target_az: str | None = None, target_alt: str | None = None) -> None:
    with _state_lock:
        if target_az is not None:
            state["target_az"] = str(target_az)
        if target_alt is not None:
            state["target_alt"] = str(target_alt)

def set_offsets(offset_az: str | None = None, offset_alt: str | None = None) -> None:
    with _state_lock:
        if offset_az is not None:
            state["offset_az"] = str(offset_az)
        if offset_alt is not None:
            state["offset_alt"] = str(offset_alt)

def set_tracking_enabled(enabled: bool) -> None:
    with _state_lock:
        state["tracking_enabled"] = bool(enabled)
        state["manual_az"] = "stop"
        state["manual_alt"] = "stop"

def set_tracking_values(current_az: float | None = None, current_alt: float | None = None) -> None:
    with _state_lock:
        if current_az is not None:
            state["current_az"] = current_az
        if current_alt is not None:
            state["current_alt"] = current_alt

def toggle_manual(axis: str, direction: str) -> str:
    if axis not in ("az", "alt"):
        raise ValueError("Axis må være 'az' eller 'alt'")
    if direction not in ("venstre", "høyre", "opp", "ned"):
        raise ValueError("Manuell retning må være 'venstre', 'høyre', 'opp' eller 'ned'")

    key = "manual_az" if axis == "az" else "manual_alt"

    with _state_lock:
        cur = state[key]
        state[key] = "stop" if cur == direction else direction
        return state[key]


def stop_all_manual() -> None:
    with _state_lock:
        state["manual_az"] = "stop"
        state["manual_alt"] = "stop"

def get_state_copy():
    with _state_lock:
        return dict(state)

def log(msg: str, level: str = "INFO"):
    line = f"{datetime.now().strftime('%H:%M:%S')} | {level} | {msg}"
    print(line, flush=True)
    with _log_lock:
        log_buffer.append(line)

def get_logs(n: int = 50):
    n = max(1, int(n))
    with _log_lock:
        return list(log_buffer)[-n:]
