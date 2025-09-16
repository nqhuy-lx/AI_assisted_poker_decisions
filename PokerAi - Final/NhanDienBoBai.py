import cv2
import numpy as np
from LoadTemplate import load_templates
from Van_Bai import VanBai

FOLDER_FOLD = "Fold"

def count_folds(screen, scale_factor, threshold=0.85):
    fold_templates = load_templates(FOLDER_FOLD)
    count = 0
    used_regions = []
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    for name, template in fold_templates.items():
        resized = template
        try:
            resized = cv2.resize(template, (0,0), fx=scale_factor, fy=scale_factor)
        except Exception:
            pass
        th, tw = resized.shape[:2]
        if screen_gray.shape[0] < th or screen_gray.shape[1] < tw:
            continue
        res = cv2.matchTemplate(screen_gray, cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED)
        locs = np.where(res >= threshold)
        for pt in zip(*locs[::-1]):
            x,y = pt
            overlap = False
            for ux, uy, uw, uh in used_regions:
                if (x < ux + uw and x + tw > ux and y < uy + uh and y + th > uy):
                    overlap = True
                    break
            if not overlap:
                used_regions.append((x,y,tw,th))
                count += 1
    return count


def update_folds(screen, scale, fold_seen, log_func=None, threshold=0.85, VanBai=None):
    fold_now = count_folds(screen, scale, threshold)
    if fold_now > fold_seen:
        delta = fold_now - fold_seen
        VanBai.cap_nhat_so_doi_thu(delta)
        fold_seen = fold_now

    so_doi_thu_con_lai = VanBai.so_doi_thu_con_lai(VanBai)
    if log_func:
        log_func(f"Số đối thủ còn lại: {so_doi_thu_con_lai}")
    return fold_seen
