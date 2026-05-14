import cv2
import numpy as np
from picamera2 import Picamera2


# Konstanter for kameraoppsett
resolution = (1920, 1080)
threshold_light = 10
minimum_sun_light = 50

# Oppsett av kamera
cam = Picamera2()
config = cam.create_still_configuration(main={"size": resolution})
cam.configure(config)


def sun_coordinates():
	regular = cam.capture_array()
	gray = cv2.cvtColor(regular, cv2.COLOR_BGR2GRAY)

	threshold = int(gray.max()) - threshold_light
	
	if threshold <= minimum_sun_light:
		return None, None

	_, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

	ys, xs = np.where(binary == 255)

	if len(xs) == 0:
		return None, None

	cx = float(np.mean(xs))
	cy = float(np.mean(ys))

	return cx, cy
