import cv2
import torch
import threading
import time
import queue
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
from math import tan, pi

# Define the Tello IP
TELLO_IP = '192.168.87.46'

# Load YOLOv5 model for object detection
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Initialize the Tello drone using TELLO_IP
tello = Tello(TELLO_IP)
tello.connect()

# Turn the video stream off and on to ensure a fresh connection
tello.streamoff()
tello.streamon()

# Setup Azure Speech Recognition
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language = "en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

frame = None
frame_lock = threading.Lock()
object_to_detect = None
desired_distance = 3  # In feet

command_queue = queue.Queue()

def recognize_once(prompt_message="Listening..."):
    print(prompt_message)
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        detected_text = result.text.lower().strip()
        print(f"Recognized: {detected_text}")
        return detected_text
    else:
        return None

def frame_capture_thread():
    """Thread function dedicated to capturing frames."""
    global frame
    frame_read = tello.get_frame_read()
    if frame_read.stopped:
        print("Failed to open video stream. Check Tello IP and connectivity.")
        tello.land()
        tello.end()
        exit()

    while True:
        with frame_lock:
            frame = frame_read.frame
        time.sleep(0.03)  # Aim for 30fps

def process_frame_thread():
    """Thread function dedicated to processing frames and making decisions."""
    global frame, object_to_detect
    frame_skip = 25  # Process every 25th frame
    frame_counter = 0

    while True:
        if frame is None:
            time.sleep(0.1)
            continue
        with frame_lock:
            temp_frame = frame.copy()

        frame_counter += 1
        if frame_counter % frame_skip == 0:
            frame_rgb = cv2.cvtColor(temp_frame, cv2.COLOR_BGR2RGB)
            results = model(temp_frame)
            labels = results.pred[0][:, -1].int()

            if object_to_detect in results.names and results.names.index(object_to_detect) in labels:
                # Logic to make the drone follow the object
                for label, score, (x1, y1, x2, y2) in results.xyxy[0]:
                    if results.names[int(label)] == object_to_detect:
                        object_width_pixel = x2 - x1
                        image_width_pixel = temp_frame.shape[1]
                        distance = (1 * image_width_pixel) / (2 * object_width_pixel * tan(30 * pi / 180))
                        if distance > desired_distance + 0.5:
                            tello.move_forward(20)
                        elif distance < desired_distance - 0.5:
                            tello.move_backward(20)

            rendered_frame = results.render()[0]
            cv2.imshow('YOLOv5', rendered_frame)
            cv2.waitKey(1)

# Start the dedicated threads
threading.Thread(target=frame_capture_thread, daemon=True).start()
threading.Thread(target=process_frame_thread, daemon=True).start()

command = recognize_once("Say 'start' to initiate object detection.")
while command != "start":
    command = recognize_once("Say 'start' to initiate object detection.")

object_to_detect = recognize_once("Verbalize the object you're seeking (e.g., 'dog').")

# Confirm that the detected object is correct
while True:
    confirmation = recognize_once(f"You mentioned: {object_to_detect}. If this is correct, say 'yes'. Otherwise, say 'no'.")
    if confirmation == "yes":
        break
    elif confirmation == "no":
        object_to_detect = recognize_once("Please verbalize the object you're seeking again.")

# Command Loop
while True:
    print("Say a command...")
    command = recognize_once()

    # Handle various commands
    if command == "oscar":
        print("Taking off...")
        tello.takeoff()
    elif command == "land":
        print("Landing...")
        tello.land()
    elif command == "apple":
        print("Going forward...")
        tello.move_forward(100)
    elif command == "back":
        print("Going back...")
        tello.move_back(100)
    elif command == "up":
        print("Going up...")
        tello.move_up(30)
    elif command == "down":
        print("Going down...")
        tello.move_down(30)
    elif command == "flip":
        print("Flipping forward...")
        tello.flip_forward()
    elif command == "chip":
        print("Flipping right...")
        tello.flip_right()
    elif command == "stop":
        print("Stopping...")
        tello.stop()
    elif command == "end":
        print("Ending...")
        break

cv2.destroyAllWindows()
tello.land()
tello.end()
