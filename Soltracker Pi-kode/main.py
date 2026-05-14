from camera import cam, sun_coordinates
from angle import current_angle_sun_to_plate
from deviation import deviation
from esp import to_esp, from_esp
from server import run_server
from server_start import enable_ap_lifecycle
import threading
import controller
import time


last_tracking_enabled = False
camera_active = False


enable_ap_lifecycle()
server = threading.Thread(
    target=run_server,
    daemon=True
)
server.start()


while True:
    state = controller.get_state_copy()
    tracking_enabled = state["tracking_enabled"]

    # Ved status-endring
    if last_tracking_enabled != tracking_enabled:
        if tracking_enabled:

            # Oppstarts-funksjoner for tracking
            if camera_active == False:
                try:
                    cam.start()
                    camera_active = True
                    controller.log("Kamera PÅ", "INFO")
                except Exception as e:
                    controller.log(f"Kamerafeil ved start: {e}", "ERROR")
                    controller.set_tracking_enabled(False)
                    last_tracking_enabled = False
                    time.sleep(1)
                    continue

        else:

            if camera_active == True:
                try:
                    cam.stop()
                    camera_active = False
                    controller.log("Kamera AV", "INFO")
                except Exception as e:
                    controller.log(f"Kamerafeil ved stop. Prøv å slå tracking På og AV igjen. Feil: {e}", "ERROR")

    # Hoved-loop
    if tracking_enabled and camera_active:

        cx, cy = sun_coordinates()
        if cx is None or cy is None:
            controller.log("Kamera fant ikke sol", "WARN")
            last_tracking_enabled = tracking_enabled
            dev_az, dev_alt = 0.0, 0.0
            time.sleep(1)
            continue

        current_az, current_alt = current_angle_sun_to_plate(cx, cy)
        controller.set_tracking_values(current_az=current_az, current_alt=current_alt)

        try:
            target_az = float(state["target_az"])
            target_alt = float(state["target_alt"])
            offset_az = float(state["offset_az"])
            offset_alt = float(state["offset_alt"])

            target_az += offset_az / 1000
            target_alt += offset_alt / 1000

        except ValueError:
            controller.log("Ugyldig inputs (må være tall)", "WARN")
            last_tracking_enabled = tracking_enabled
            controller.set_tracking_enabled(False)
            time.sleep(1)
            continue

        dev_az, dev_alt = deviation(current_az, current_alt, target_az, target_alt)

    else:
        if state["manual_az"] == "høyre":
            dev_az = -50.0
        elif state["manual_az"] == "venstre":
            dev_az = 50.0
        else:
            dev_az = 0.0

        if state["manual_alt"] == "opp":
            dev_alt = 50.0
        elif state["manual_alt"] == "ned":
            dev_alt = -50.0
        else:
            dev_alt = 0.0

        time.sleep(0.9)

    to_esp(dev_az, dev_alt, tracking_enabled)
    
    # Meldinger fra ESP
    message_esp = from_esp()
    if message_esp is not None:
        controller.log(f"From ESP: {message_esp}")
    
    last_tracking_enabled = tracking_enabled
    
    time.sleep(0.05)
    
