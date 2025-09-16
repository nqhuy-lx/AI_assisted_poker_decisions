import cv2
import os

def load_templates(folder):
    templates = {}
    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg")):
            path = os.path.join(folder, filename)
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is not None:
                key = os.path.splitext(filename)[0]
                templates[key] = img
    return templates
