import time
import cv2
import torch
import threading
import queue
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk



# Constants
TELLO_IP = '192.168.86.27'

# Setup YOLOv5

# Paths (change these paths as per your system)
weights_path = "C:\\Users\\sbarr\\Downloads\\Summer-Drone-Capstone\\Capstone-2023---Drones\\yolov5\\runs\\train\\steve_model23\\weights\\best.pt"

# Setup YOLOv5 with custom model weights
model = torch.hub.load('./yolov5', 'custom', path=weights_path, source='local')  # 'source' set to 'local' means don't download anything but use local files

# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Tello Setup
tello = Tello(TELLO_IP)
tello.connect()
tello.streamoff()
tello.streamon()

# Azure Speech Recognition Setup
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language = "en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

def get_command():
    """Listen for a voice command and return the command string."""
    try:
        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {result.text.lower()}")
            return result.text.lower()
        else:
            return None
    except Exception as e:
        print(f"Error in get_command: {e}")
        return None

print("Say 'start' to initiate object detection.")
command = get_command()
while command != "start.":
    command = get_command()

# Create a queue and thread for displaying frames
frame_queue = queue.Queue(maxsize=5)

def display_frame(frame_queue):
    while True:
        frame = frame_queue.get()
        if frame is None:
            break
        cv2.imshow('YOLOv5', frame)
        cv2.waitKey(1)

display_thread = threading.Thread(target=display_frame, args=(frame_queue,))
display_thread.start()

frame_read = tello.get_frame_read()
frame_skip = 10
frame_counter = 0

while True:
    frame = frame_read.frame
    frame_counter += 1
    
    time.sleep(0.1)  # introduce a delay of 0.1 seconds

    if frame_counter % frame_skip == 0:
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(frame_rgb)
            rendered_frame = results.render()[0]
            frame_queue.put(rendered_frame)
        except Exception as e:
            print(f"Error processing frame: {e}")

    command = get_command()

    if command:
        if command == "up.":
            tello.move_up(30)
        elif command == "down.":
            tello.move_down(30)
        elif command == "left.":
            tello.move_left(30)
        elif command == "right.":
            tello.move_right(30)
        elif command == "forward.":
            tello.move_forward(30)
        elif command == "back.":
            tello.move_back(30)
        elif command == "blue pumpkin.":
            tello.takeoff()
        elif command == "land.":
            tello.land()
        elif command == "stop.":
            break

# Cleanup
frame_queue.put(None)
display_thread.join()
cv2.destroyAllWindows()
tello.land()
tello.end()
