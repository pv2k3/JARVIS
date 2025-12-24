import cv2
import os
import time
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

# User task
task = input("Enter robot task (example: move until you see a door): ")

# Open camera
cap = cv2.VideoCapture("http://192.168.1.3:8080/video")

def send_frame_to_gemini(frame, task):
    # Convert OpenCV image to PIL
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb)

    prompt = f"""
You are a robot vision and navigation system.

Task: {task}

Instructions:
1. Identify objects visible in the image.
2. Decide movement direction based on task.
3. Avoid obstacles.

Respond ONLY in this format:
Objects: <comma separated>
Direction: forward / left / right / stop
"""

    response = model.generate_content([prompt, image])
    return response.text.lower()

print("\nRobot with vision started. Press Q to quit.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Send frame to Gemini every 1 second (avoid API spam)
    decision_text = send_frame_to_gemini(frame, task)
    print("\nGemini Response:\n", decision_text)

    # Extract direction
    direction = "stop"
    for d in ["forward", "left", "right", "stop"]:
        if d in decision_text:
            direction = d
            break

    print("Movement Decision:", direction)

    cv2.imshow("Camera Feed", frame)

    if direction == "stop":
        print("Task completed or unsafe to proceed.")
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(1)  # limit API calls

cap.release()
cv2.destroyAllWindows()
