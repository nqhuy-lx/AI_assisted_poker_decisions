import os
import cv2
import pyautogui
import numpy as np
from datetime import datetime

from NhanDienLaBai import capture_screen

def save_game_result(folder_name, game_number, log_text):
    base_dir = os.path.join(os.getcwd(), "PokerResults")
    save_dir = os.path.join(base_dir, folder_name)
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"game_{game_number}_{timestamp}"

    txt_path = os.path.join(save_dir, base_filename + ".txt")
    img_path = os.path.join(save_dir, base_filename + ".png")

    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(log_text)
        print(f"[SaveResult] Đã lưu log: {txt_path}")
    except Exception as e:
        print(f"[SaveResult] Lỗi khi lưu log: {e}")

    try:
        img = capture_screen()
        cv2.imwrite(img_path, img)
        print(f"[SaveResult] Đã lưu ảnh: {img_path}")
    except Exception as e:
        print(f"[SaveResult] Lỗi khi lưu ảnh: {e}")

    return txt_path, img_path
