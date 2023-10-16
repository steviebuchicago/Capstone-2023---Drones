import cv2
import torch
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
import time

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

def get_command():
    """Function to recognize and return a speech command."""
    try:
        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {result.text.lower()}")
            return result.text.lower()
    except Exception as e:
        print(f"Error in get_command: {e}")
    return None

# Prompt the user verbally to start object detection
print("Say 'start' to initiate object detection.")
command = get_command()

# Wait for the 'start' command
while command != "start.":
    command = get_command()

# Prompt user to say the name of the object they want to detect
print("Verbalize the object you're seeking (e.g., 'dog').")
object_to_detect = get_command()

# Confirm that the detected object is correct
print(f"You mentioned: {object_to_detect}. If this is correct, say 'yes'. Otherwise, say 'no'.")
confirmation = get_command()
while confirmation not in ["yes.", "no."]:
    print("Didn't catch that. Please say 'yes' or 'no'.")
    confirmation = get_command()

# If user disagrees with detected object, prompt again until they confirm
while confirmation == "no.":
    print("Please verbalize the object you're seeking again.")
    object_to_detect = get_command()
    print(f"You mentioned: {object_to_detect}. If this is correct, say 'yes'. Otherwise, say 'no'.")
    confirmation = get_command()
    while confirmation not in ["yes.", "no."]:
        print("Didn't catch that. Please say 'yes' or 'no'.")
        confirmation = get_command()

print(f"Loading the libraries to scan for: {object_to_detect}")

# Start video capture. Try to acquire the video stream from the Tello.
frame_read = tello.get_frame_read()
if frame_read.stopped:
    print("Failed to open video stream. Check Tello IP and connectivity.")
    tello.land()
    tello.end()
    exit()

flying = False
command_check_interval = 50  # check command every 50 frames
frame_counter = 0

# Start object detection and drone command loop
while True:
    try:
        frame = frame_read.frame
        if frame is None:
            print("Failed to retrieve frame. Check Tello connection.")
            continue
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect objects in the frame using YOLOv5
        results = model(frame_rgb)
        labels = results.pred[0][:, -1].int()

        # Check if the desired object is detected
        if object_to_detect in results.names and results.names.index(object_to_detect) in labels:
            print(f"{object_to_detect.capitalize()} detected!")

        # Display the frame with detected objects
        rendered_frame = results.render()[0]
        cv2.imshow('YOLOv5', rendered_frame)
        cv2.waitKey(1)  # Add this line

        # Listen for command every 'command_check_interval' frames
        if frame_counter % command_check_interval == 0:
            print("Say a command...")
            command = get_command()

        # Handle various commands
        # The following commands can be used to control the drone based on recognized speech
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

    except Exception as e:
        print(f"Error processing frame: {e}")
        continue

cv2.destroyAllWindows()
tello.land()
tello.end()
