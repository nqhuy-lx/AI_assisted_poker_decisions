import cv2
import numpy as np

def estimate_scale(screen, icon_template, search_scales=None):
    if search_scales is None:
        search_scales = np.linspace(0.50, 1.50, 41)
    best_scale, best_val = 1.00, -1
    icon_gray = cv2.cvtColor(icon_template, cv2.COLOR_BGR2GRAY)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    for scale in search_scales:
        resized = cv2.resize(icon_gray, (0, 0), fx=scale, fy=scale)
        if screen_gray.shape[0] < resized.shape[0] or screen_gray.shape[1] < resized.shape[1]:
            continue
        res = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > best_val:
            best_val = max_val
            best_scale = scale
    return best_scale