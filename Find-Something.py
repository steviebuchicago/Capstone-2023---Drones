# Automated Find my ...

import cv2
import torch
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
import time

# Load YOLOv5 modeldog
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Initialize Tello
tello = Tello('192.168.87.46')
tello.connect()

# Setup Azure Speech Recognition
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language = "en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

def get_command():
    try:
        result = speech_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {result.text.lower()}")
            return result.text.lower()
    
    except Exception as e:
        print(f"Error in get_command: {e}")
    
    return None

# Prompt user for the object to detect
object_to_detect = input("Enter the object you want to detect (e.g., dog): ")

print("Say 'start' to begin.")
while True:
    command = get_command()
    if command == "start.":
        print("Ready for commands...")
        break

cap = cv2.VideoCapture(0)
flying = False

while True:
    ret, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = model(frame_rgb)
    labels = results.pred[0][:, -1].int()

    if object_to_detect in results.names and results.names.index(object_to_detect) in labels:
        print(f"{object_to_detect.capitalize()} detected!")
    
    # Display the frame with detected objects
    rendered_frame = results.render()[0]
    cv2.imshow('YOLOv5', rendered_frame)

    print("Say a command...")
    command = get_command()

    if command == "oscar." and not flying:
        print("Taking off...")
        flying = True
        tello.takeoff()
  
    elif command == "land." and flying:
        print("Landing...")
        flying = False
        tello.land()

    elif command == "apple.":
        print("Going forward...")
        tello.move_forward(100)

    elif command == "back.":
        print("Going back...")
        tello.move_back(100)

    elif command == "up.":
        print("Going up...")
        tello.move_up(30)

    elif command == "down.":
        print("Going down...")
        tello.move_down(30)

    elif command == "flip.":
        print("Flipping forward...")
        tello.flip_forward()

    elif command == "chip.":
        print("Flipping right...")
        tello.flip_right()

    elif command == "stop.":
        print("Stopping...")
        tello.stop()

    elif command == "end.":
        print("Ending...")
        break

    time.sleep(2)

cap.release()
cv2.destroyAllWindows()
tello.land()
tello.end()
