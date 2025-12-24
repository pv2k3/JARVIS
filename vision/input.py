import cv2
from PIL import Image
import pyautogui
import numpy as np
import os
import time

cap = cv2.VideoCapture(0)
os.makedirs("../database/images", exist_ok=True)

def compress_and_save(pil_img, prefix):
    pil_img = pil_img.resize((800, 450))
    filename = f"{prefix}_{int(time.time())}.jpg"
    path = os.path.join("images", filename)
    pil_img.save(path, "JPEG", quality=80)
    return pil_img, path


def capture_camera():
    ret, frame = cap.read()
    if not ret:
        return None, None

    cv2.imshow("📷 Camera Capture", frame)
    cv2.waitKey(800)
    cv2.destroyWindow("📷 Camera Capture")

    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return compress_and_save(pil_img, "camera")


def capture_screenshot():
    screenshot = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    h, w, _ = frame.shape
    cv2.rectangle(frame, (10, 10), (w - 10, h - 10), (0, 255, 0), 3)

    cv2.imshow("🖥️ Screenshot", frame)
    cv2.waitKey(800)
    cv2.destroyWindow("🖥️ Screenshot")

    return compress_and_save(screenshot, "screen")




if __name__ == "__main__":
    capture_camera()
    capture_screenshot()