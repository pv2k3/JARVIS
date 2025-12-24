import os
import cv2
import pyautogui
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import json
from datetime import datetime




# =========================
# LOAD ENV & CONFIGURE GEMINI
# =========================
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-2.5-pro"
)


# =========================
# TOKEN ESTIMATION & LOGGING
# =========================
LOG_FILE = "gemini_token_log.jsonl"

def estimate_tokens(text):
    if not text:
        return 0
    return max(1, len(text) // 4)

def log_tokens(action, prompt_text, response_text):
    input_tokens = estimate_tokens(prompt_text)
    output_tokens = estimate_tokens(response_text)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "input_tokens_est": input_tokens,
        "output_tokens_est": output_tokens,
        "total_tokens_est": input_tokens + output_tokens
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


# =========================
# CAMERA SETUP
# =========================
cap = cv2.VideoCapture(0)

# =========================
# MEMORY
# =========================
chat_history = []
MAX_HISTORY = 10

# =========================
# IMAGE TOOLS
# =========================
def capture_camera():
    ret, frame = cap.read()
    if not ret:
        return None
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)

def capture_screenshot():
    return pyautogui.screenshot()

# =========================
# ASK GEMINI WHAT TO DO
# =========================
def decide_action(user_input):
    history_text = "\n".join(chat_history)

    prompt = f"""
You are an AI agent controller.

Conversation history:
{history_text}

User input:
{user_input}

Decide the next action.

Available actions:
- CHAT (text only)
- CAMERA (use webcam)
- SCREENSHOT (capture screen)
- STOP (end session)

Respond in EXACTLY this JSON format:
{{
  "action": "<CHAT | CAMERA | SCREENSHOT | STOP>",
  "reason": "<short reason>"
}}
"""
    response = model.generate_content(prompt)
    text = response.text.strip()

    log_tokens(
        action="DECISION",
        prompt_text=prompt,
        response_text=text
    )

    # Basic JSON extraction (safe/simple)
    action = "CHAT"
    for a in ["CHAT", "CAMERA", "SCREENSHOT", "STOP"]:
        if a in text:
            action = a
            break

    return action, text

# =========================
# SEND RESULT BACK TO GEMINI
# =========================
def respond_with_result(user_input, action, action_result=None):
    history_text = "\n".join(chat_history)

    prompt = f"""
You are an intelligent assistant.

Conversation history:
{history_text}

User input:
{user_input}

Action performed:
{action}

Action result:
{action_result}

Provide a helpful response to the user.
"""
    if isinstance(action_result, Image.Image):
        response = model.generate_content([prompt, action_result])
    else:
        response = model.generate_content(prompt)

    reply_text = response.text.strip()

    log_tokens(
        action=action,
        prompt_text=prompt,
        response_text=reply_text
    )

    return reply_text

# =========================
# MAIN LOOP
# =========================
print("\n🤖 Gemini 2.5 Pro Agent Controller Started")
print("Gemini decides actions dynamically")
print("Type 'exit' to stop\n")

while True:
    user_input = input("You: ")

    action, decision_raw = decide_action(user_input)
    print(f"\n[Decision] {decision_raw}")

    # -------- STOP --------
    if action == "STOP":
        print("Agent: Shutting down. Goodbye!")
        break

    # -------- CAMERA --------
    elif action == "CAMERA":
        image = capture_camera()
        if image is None:
            reply = "Camera could not be accessed."
        else:
            reply = respond_with_result(user_input, action, image)

    # -------- SCREENSHOT --------
    elif action == "SCREENSHOT":
        image = capture_screenshot()
        reply = respond_with_result(user_input, action, image)

    # -------- CHAT --------
    else:
        reply = respond_with_result(user_input, action)

    print("Agent:", reply)

    # -------- UPDATE MEMORY --------
    chat_history.append(f"User: {user_input}")
    chat_history.append(f"Assistant: {reply}")

    if len(chat_history) > MAX_HISTORY:
        chat_history = chat_history[-MAX_HISTORY:]

cap.release()
