import os
import cv2
import base64
import pyautogui
import requests
from PIL import Image
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()
# ============================================================
# 1. HF API CONFIG
# ============================================================

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = "llava-hf/llava-1.5-7b-hf"
HF_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"


HF_HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

# ============================================================
# 2. SHORT-TERM MEMORY
# ============================================================

memory = []
MAX_MEMORY_LINES = 6

def update_memory(user, assistant):
    memory.append(f"U:{user}")
    memory.append(f"A:{assistant}")
    if len(memory) > MAX_MEMORY_LINES:
        memory[:] = memory[-MAX_MEMORY_LINES:]

# ============================================================
# 3. OLLAMA INTENT DETECTION (UNCHANGED)
# ============================================================

def detect_intent(user_input):
    prompt = (
        f"You are an intent classifier. "
        f"Classify the message \"{user_input}\" into EXACTLY ONE of "
        f"[CHAT, CAMERA, SCREENSHOT, STOP]. "
        f"Rules: CAMERA=seeing/looking/webcam; "
        f"SCREENSHOT=screen/UI; "
        f"STOP=exit/quit; "
        f"default CHAT. Output ONLY one word."
    )

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:0.6b",
                "prompt": prompt,
                "stream": False
            },
            timeout=5
        ).json()

        text = res.get("response", "").upper()
        for intent in ["CHAT", "CAMERA", "SCREENSHOT", "STOP"]:
            if intent in text:
                return intent
    except Exception:
        pass

    return "CHAT"

# ============================================================
# 4. IMAGE SOURCES
# ============================================================

def capture_camera():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return image

def capture_screenshot():
    return pyautogui.screenshot().convert("RGB")

def image_to_base64(image: Image.Image):
    buf = BytesIO()
    image.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# ============================================================
# 5. HF API RESPONSE (TEXT + IMAGE)
# ============================================================

def hf_respond(user_prompt, image=None, debug=True):
    context = "\n".join(memory)

    prompt = f"""
You are a helpful assistant.
Use the image if provided.

Context:
{context}

User: {user_prompt}
"""

    if image:
        payload = {
            "inputs": {
                "text": prompt,
                "image": image_to_base64(image)
            },
            "parameters": {
                "max_new_tokens": 200
            }
        }
    else:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200
            }
        }

    try:
        response = requests.post(
            HF_URL,
            headers=HF_HEADERS,
            json=payload,
            timeout=120
        )
    except requests.exceptions.RequestException as e:
        return f"[HF ERROR] Network error: {e}"

    # ---------- HTTP-LEVEL ERRORS ----------
    if response.status_code != 200:
        try:
            error_json = response.json()
        except Exception:
            return f"[HF ERROR] HTTP {response.status_code}: {response.text}"

        # Hugging Face standard error formats
        if "error" in error_json:
            return f"[HF ERROR] {error_json['error']}"

        if "estimated_time" in error_json:
            return (
                "[HF INFO] Model is loading on Hugging Face servers.\n"
                f"Estimated time: {error_json['estimated_time']} seconds.\n"
                "Please retry shortly."
            )

        return f"[HF ERROR] HTTP {response.status_code}: {error_json}"

    # ---------- SUCCESS PATH ----------
    try:
        result = response.json()
    except Exception as e:
        return f"[HF ERROR] Failed to parse JSON response: {e}"

    if debug:
        print("\n[HF DEBUG RESPONSE]")
        print(result)

    # ---------- EXPECTED SUCCESS FORMAT ----------
    if isinstance(result, list) and len(result) > 0:
        if "generated_text" in result[0]:
            return result[0]["generated_text"].strip()

    # ---------- FALLBACK WITH DETAILS ----------
    return (
        "[HF ERROR] Unable to generate response.\n"
        f"Raw response: {result}"
    )


# ============================================================
# 6. MAIN AGENT LOOP
# ============================================================

print("\n🤖 Hybrid AI Agent Started (API Mode)")
print("Ollama (intent) + HF Vision API")
print("Type 'exit' to stop\n")

while True:
    user_input = input("You: ")

    intent = detect_intent(user_input)
    print(f"[Intent → {intent}]")

    if intent == "STOP":
        print("Agent: Goodbye 👋")
        break

    elif intent == "CAMERA":
        image = capture_camera()
        reply = hf_respond(user_input, image=image) if image else "Camera not available."

    elif intent == "SCREENSHOT":
        image = capture_screenshot()
        reply = hf_respond(user_input, image=image)

    else:  # CHAT
        reply = hf_respond(user_input)

    print("Agent:", reply)
    update_memory(user_input, reply)
