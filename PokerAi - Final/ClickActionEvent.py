import cv2
import numpy as np
import pyautogui
import time

from LoadTemplate import load_templates
from NhanDienLaBai import capture_screen
from SaveResult import save_game_result 

BUTTON_FOLDER = "Buttons"
RESULT_FOLDER = "Results"


class ButtonClicker:
    def __init__(self):
        self.positions = {}

    def find_button(self, name, scale, fileName):
        if name in self.positions:
            return self.positions[name]

        screen = capture_screen()
        templates = load_templates(fileName)
        if name not in templates:
            print(f"⚠️ Không tìm thấy template nút {name}")
            return None

        template = templates[name]
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        resized = cv2.resize(template_gray, (0, 0), fx=scale, fy=scale)
        res = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val < 0.8:
            print(f"❌ Không khớp đủ mạnh cho nút {name} ({max_val:.2f})")
            return None

        x, y = max_loc
        h, w = resized.shape
        center = (x + w // 2, y + h // 2)

        self.positions[name] = center
        return center

    def click_button(self, name, scale, wait_until_found=True, delay=0.5):
        pos = None
        t0 = time.time()
        while pos is None:
            pos = self.find_button(name, scale, BUTTON_FOLDER)
            if pos or not wait_until_found:
                break
            if time.time() - t0 > 10:
                print(f"❌ Timeout tìm nút {name}")
                return False
            time.sleep(0.5)

        if pos:
            pyautogui.click(pos[0], pos[1])
            time.sleep(delay)
            return True
        return False
    
    def wait(self, scale, timeout=20):
        results = load_templates(RESULT_FOLDER)
        t0 = time.time()

        while time.time() - t0 < timeout:
            screen = capture_screen()
            screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

            for name, template in results.items():
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(template_gray, (0, 0), fx=scale, fy=scale)

                res = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)

                if max_val >= 0.5:
                    print(f"✅ Nhận diện kết quả: {name} ({max_val:.2f})")
                    return True

            print("⏳ Chưa thấy màn hình kết quả, thử lại...")
            time.sleep(1)

        print("❌ Timeout: không thấy màn hình kết quả")
        return False

def wait_result_and_restart(scale, folder_name, game_number, log_text, timeout=60):
    results = load_templates(RESULT_FOLDER)
    t0 = time.time()

    while time.time() - t0 < timeout:
        screen = capture_screen()
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        for name, template in results.items():
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(template_gray, (0, 0), fx=scale, fy=scale)

            res = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val >= 0.5:
                print(f"✅ Nhận diện kết quả: {name} ({max_val:.2f})")

                save_game_result(folder_name, game_number, log_text)

                x, y = max_loc
                h, w = resized.shape
                center = (x + w // 2, y + h // 2)
                time.sleep(7)
                pyautogui.click(center[0], center[1])
                return True

        print("⏳ Chưa thấy màn hình kết quả, thử lại...")
        time.sleep(1)

    print("❌ Timeout: không thấy màn hình kết quả")
    return False