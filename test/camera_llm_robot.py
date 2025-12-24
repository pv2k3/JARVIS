import cv2
from transformers import pipeline

# Load Hugging Face model
llm = pipeline(
    "text-generation",
    model="google/flan-t5-base"
)

# Get user task
task = input("Enter robot task (example: go to open area): ")

# Open camera
cap = cv2.VideoCapture("http://192.168.1.3:8080/video")

def get_zone_brightness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    left = gray[:, :w//3].mean()
    center = gray[:, w//3:2*w//3].mean()
    right = gray[:, 2*w//3:].mean()

    return left, center, right

def ask_llm(left, center, right, task):
    prompt = f"""
Task: {task}

Camera info:
Left zone brightness: {left}
Center zone brightness: {center}
Right zone brightness: {right}

Rule:
- Dark = obstacle
- Bright = free

Answer ONLY one word:
forward, left, right, stop
"""
    response = llm(prompt, max_new_tokens=5)[0]["generated_text"].lower()

    for d in ["forward", "left", "right", "stop"]:
        if d in response:
            return d
    return "stop"

print("Robot started. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    left, center, right = get_zone_brightness(frame)
    decision = ask_llm(left, center, right, task)

    print("Decision:", decision)

    cv2.imshow("Camera Feed", frame)

    if decision == "stop":
        print("Task completed or no safe path.")
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
