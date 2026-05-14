import cv2
import numpy as np
import math
import os

MOUNT_ANGLE = 30

data = np.load(os.path.expanduser("~/calib/calibration.npz"))
K = data["K"]
dist = data["dist"]

def current_angle_sun_to_plate(cx, cy):
    if cx is None or cy is None:
        return None, None

    pts = np.array([[[cx, cy]]], dtype=np.float64)
    undistorted = cv2.undistortPoints(pts, K, dist)

    x = undistorted[0, 0, 0]
    y = undistorted[0, 0, 1]

    current_az = math.degrees(math.atan(x))
    current_alt = 90 + math.degrees(math.atan(-y)) - MOUNT_ANGLE

    return current_az, current_alt
