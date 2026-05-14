import logging
from flask import Flask, request, jsonify, send_from_directory
import subprocess

import controller

app = Flask(__name__)

logging.getLogger("werkzeug").setLevel(logging.ERROR)

@app.get("/")
def index():
    return send_from_directory("static", "index.html")

@app.get("/api/state")
def api_state():
    return jsonify(controller.get_state_copy())

@app.post("/api/targets")
def api_targets():
    data = request.get_json(force=True) or {}
    controller.set_targets(data.get("target_az"), data.get("target_alt"))
    controller.set_offsets(data.get("offset_az") or "0", data.get("offset_alt") or "0")
    controller.log("Oppdaterte variabler")
    return jsonify({"ok": True})

@app.post("/api/tracking")
def api_tracking():
    data = request.get_json(force=True) or {}
    enabled = bool(data.get("enabled", False))
    controller.set_tracking_enabled(enabled)
    controller.log("Tracking PÅ" if enabled else "Tracking AV")
    return jsonify({"ok": True, "tracking_enabled": enabled})

@app.get("/api/logs")
def api_logs():
    n = request.args.get("n", 50)
    try:
        n_int = int(n)
    except Exception:
        n_int = 50
    return jsonify({"logs": controller.get_logs(n_int)})

@app.post("/api/manual/toggle")
def api_manual_toggle():
    state = controller.get_state_copy()
    if state["tracking_enabled"]:
        return jsonify({"ok": False, "error": "Tracking er PÅ"}), 409

    data = request.get_json(force=True) or {}
    axis = str(data.get("axis", "")).lower()     # "az" eller "alt"
    direction = str(data.get("dir", "")).lower() # "up" eller "down"

    try:
        new_state = controller.toggle_manual(axis, direction)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    controller.log(f"Manuell: {axis.upper()} -> {new_state.upper()}")
    return jsonify({"ok": True})


@app.post("/api/manual/stop_all")
def api_manual_stop_all():
    state = controller.get_state_copy()
    if state["tracking_enabled"]:
        return jsonify({"ok": False, "error": "Tracking er PÅ"}), 409

    controller.stop_all_manual()
    controller.log("Manuell: STOPP ALLE", "INFO")
    return jsonify({"ok": True})

@app.post("/api/shutdown")
def api_shutdown():
    state = controller.get_state_copy()

    # Ikke lov hvis tracking er PÅ
    if state["tracking_enabled"]:
        controller.log("Shutdown forsøkt mens tracking var PÅ", "WARN")
        return jsonify({"ok": False, "error": "Tracking er PÅ. Slå av tracking først."}), 409

    # Ikke lov hvis manuell styring er aktiv
    if state["manual_az"] != "stop" or state["manual_alt"] != "stop":
        controller.log("Shutdown forsøkt mens manuell styring var aktiv", "WARN")
        return jsonify({"ok": False, "error": "Manuell styring må stå i STOP før shutdown."}), 409

    controller.log("Shutdown trigget", "WARN")
    subprocess.Popen(["sudo", "/sbin/shutdown", "-h", "now"])
    return jsonify({"ok": True})

def run_server(host: str = "0.0.0.0", port: int = 5000):
    controller.log("Webserver startet")
    app.run(host=host, port=port, debug=False, use_reloader=False)