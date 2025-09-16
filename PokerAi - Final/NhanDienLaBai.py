import cv2
import numpy as np
import pyautogui

from LoadTemplate import load_templates

FOLDER_LEFT = "Trai"
FOLDER_RIGHT = "Phai"
FOLDER_52 = "Thang"

def capture_screen():
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img

def _norm_name(name: str) -> str:
    if not name:
        return None
    parts = name.split("_")
    if parts[-1].lower() in ["trai", "phai"]:
        parts = parts[:-1]
    if len(parts) >= 2:
        suit = parts[0].capitalize()
        rank = parts[1].upper()
        return f"{rank}_{suit}"
    return name.replace(" ", "_")

def recognize_card(screen_gray, templates, scales, used_regions=[]):
    best_card, best_val, best_loc, best_shape = None, -1, None, None
    for name, template in templates.items():
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        for scale in scales:
            resized = cv2.resize(template_gray, (0,0), fx=scale, fy=scale)
            th, tw = resized.shape
            if screen_gray.shape[0] < th or screen_gray.shape[1] < tw:
                continue
            res = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            x,y = max_loc
            overlap = False
            for ux, uy, uw, uh in used_regions:
                if (x < ux + uw and x + tw > ux and y < uy + uh and y + th > uy):
                    overlap = True
                    break
            if overlap:
                continue
            if max_val > best_val:
                best_card, best_val, best_loc, best_shape = name, max_val, max_loc, (tw, th)
    if best_val < 0.8:
        return None, None, None, None
    return best_card, best_val, best_loc, best_shape

def recognize_hand(screen, scale_factor):
    left_templates = load_templates(FOLDER_LEFT)
    right_templates = load_templates(FOLDER_RIGHT)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    scales = [scale_factor]
    left_card, _, _, _ = recognize_card(screen_gray, left_templates, scales)
    right_card, _, _, _ = recognize_card(screen_gray, right_templates, scales)
    return _norm_name(left_card) if left_card else None, _norm_name(right_card) if right_card else None

def recognize_board(screen, num_cards, scale_factor, exclude=None, used_regions=None):
    if used_regions is None:
        used_regions = []
    if exclude is None:
        exclude = []
    templates = load_templates(FOLDER_52)
    for ex in exclude:
        if ex is None: 
            continue
        templates.pop(str(ex), None)

    found = []
    scales = [scale_factor * 0.75 ,scale_factor * 0.825, scale_factor, scale_factor * 1.125, scale_factor * 1.25]
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    for i in range(num_cards):
        if not templates:
            break
        card, val, loc, shape = recognize_card(screen_gray, templates, scales, used_regions)
        if not card:
            break
        found.append(_norm_name(card))
        templates.pop(card, None)
        if loc and shape:
            x,y = loc; w,h = shape
            used_regions.append((x,y,w,h))
    return found
