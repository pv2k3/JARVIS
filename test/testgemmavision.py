import pyautogui
import requests
import base64
from io import BytesIO
import cv2

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"


def take_screenshot():
    img = pyautogui.screenshot()
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def take_camera_image(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Camera not accessible")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Failed to capture image from camera")

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    success, buffer = cv2.imencode(".png", frame_rgb)
    if not success:
        raise RuntimeError("Failed to encode camera image")

    return buffer.tobytes()


def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")


def ask_ollama_with_image(prompt, image_bytes):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [image_to_base64(image_bytes)],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["response"]


if __name__ == "__main__":

    print("Select input source:")
    print("1 → Screenshot")
    print("2 → Camera")
    choice = input("Enter choice (1/2): ").strip()

    if choice == "1":
        print("📸 Taking screenshot...")
        image_bytes = take_screenshot()
    elif choice == "2":
        print("📷 Capturing camera image...")
        image_bytes = take_camera_image()
    else:
        raise ValueError("Invalid choice")

    user_question = input("\n❓ Ask something about the image: ")

    print("\n🧠 Sending image to Ollama...")
    result = ask_ollama_with_image(user_question, image_bytes)

    print("\n🧾 Ollama Response:\n")
    print(result)
