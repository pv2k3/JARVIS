# ============================================================
# 🤖 HYBRID AI AGENT
# Local Ollama (Intent) + Gemini 2.5 Pro (Reasoning/Vision)
# ============================================================

import os
import time
import cv2
import requests
import pyautogui
import numpy as np
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# ============================================================
# 1. ENVIRONMENT SETUP
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-2.5-pro")

# ============================================================
# 2. INITIALIZE RESOURCES
# ============================================================

cap = cv2.VideoCapture(0)
os.makedirs("images", exist_ok=True)

# ============================================================
# 3. SHORT-TERM MEMORY (TOKEN SAFE)
# ============================================================

memory = []
MAX_MEMORY_LINES = 6

def update_memory(user, assistant):
    memory.append(f"U:{user}")
    memory.append(f"A:{assistant}")
    if len(memory) > MAX_MEMORY_LINES:
        memory[:] = memory[-MAX_MEMORY_LINES:]

# ============================================================
# 4. LOCAL OLLAMA INTENT DETECTION (CHEAP)
# ============================================================

def detect_intent_local(user_input):
    # 🔹 SINGLE-LINE, PROMPT-ENGINEERED INTENT PROMPT
    prompt = (
        f"You are an intent classification system. Classify the user message "
        f"\"{user_input}\" into EXACTLY ONE intent from [CHAT, CAMERA, SCREENSHOT, STOP]. "
        f"Rules: CAMERA=seeing/looking/objects in front/webcam; SCREENSHOT=screen/window/UI/desktop; "
        f"STOP=exit/quit/shutdown; if unsure choose CHAT. "
        f"Output ONLY one word, no explanations."
    )

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:0.6b",
                "prompt": prompt,
                "stream": False
            },
            timeout=10
        ).json()

        text = res.get("response", "").upper()
        for intent in ["CHAT", "CAMERA", "SCREENSHOT", "STOP"]:
            if intent in text:
                return intent
    except Exception as e:
        print("[WARN] Ollama intent detection failed:", e)

    return "CHAT"

# ============================================================
# 5. IMAGE UTILITIES (COMPRESS + SAVE)
# ============================================================

def compress_and_save(pil_img, prefix):
    pil_img = pil_img.resize((640, 360))
    filename = f"{prefix}_{int(time.time())}.jpg"
    path = os.path.join("images", filename)
    pil_img.save(path, "JPEG", quality=75)
    return pil_img, path

# ============================================================
# 6. CAMERA CAPTURE (WITH PREVIEW)
# ============================================================

def capture_camera():
    ret, frame = cap.read()
    if not ret:
        return None, None

    cv2.imshow("📷 Camera Capture", frame)
    cv2.waitKey(800)
    cv2.destroyWindow("📷 Camera Capture")

    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return compress_and_save(pil_img, "camera")

# ============================================================
# 7. SCREENSHOT CAPTURE (WITH OUTLINE)
# ============================================================

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    h, w, _ = frame.shape
    cv2.rectangle(frame, (10, 10), (w - 10, h - 10), (0, 255, 0), 3)

    cv2.imshow("🖥️ Screenshot", frame)
    cv2.waitKey(800)
    cv2.destroyWindow("🖥️ Screenshot")

    return compress_and_save(screenshot, "screen")

# ============================================================
# 8. GEMINI RESPONSE (TOKEN OPTIMIZED)
# ============================================================

def gemini_respond(user_input, image=None):
    context = "\n".join(memory)

    prompt = f"""
You are a helpful assistant.

Recent context:
{context}

User:
{user_input}

Reply briefly and clearly.
"""

    if image:
        response = gemini.generate_content([prompt, image])
    else:
        response = gemini.generate_content(prompt)

    return response.text.strip()

# ============================================================
# 9. MAIN AGENT LOOP
# ============================================================

print("\n🤖 Hybrid AI Agent Started")
print("Local Ollama (intent) + Gemini 2.5 Pro (vision/reasoning)")
print("Type 'exit' to stop\n")

while True:
    user_input = input("You: ")

    intent = detect_intent_local(user_input)
    print(f"[Intent → {intent}]")

    if intent == "STOP":
        print("Agent: Shutting down. Goodbye 👋")
        break

    elif intent == "CAMERA":
        img, path = capture_camera()
        if img:
            reply = gemini_respond(user_input, img)
        else:
            reply = "Camera not available."

    elif intent == "SCREENSHOT":
        img, path = capture_screenshot()
        if img:
            reply = gemini_respond(user_input, img)
        else:
            reply = "Screenshot failed."

    else:  # CHAT
        reply = gemini_respond(user_input)

    print("Agent:", reply)
    update_memory(user_input, reply)

# ============================================================
# 10. CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()
