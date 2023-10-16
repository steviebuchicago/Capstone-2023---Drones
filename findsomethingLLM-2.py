#FindSomethingLLM-2.py

#  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
#  speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")

import cv2
import torch
import threading
import queue
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
import openai

# Constants
TELLO_IP = '192.168.86.42'
OPENAI_API_KEY = "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"

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Setup YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Tello Drone Setup
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

def process_advanced_command(command):
    """Use GPT-3.5 to generate a response for the advanced command."""
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"How should a drone respond to the command: '{command}'?",
        max_tokens=150
    )
    return response.choices[0].text.strip()

frame_queue = queue.Queue(maxsize=5)
frame_read = tello.get_frame_read()

def display_frame():
    while True:
        frame = frame_queue.get()
        if frame is None:
            break
        cv2.imshow('YOLOv5', frame)
        cv2.waitKey(1)

display_thread = threading.Thread(target=display_frame)
display_thread.start()

print("Voice command your drone! Start with 'takeoff' and control as you like.")

while True:
    frame = frame_read.frame
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(frame_rgb)
    rendered_frame = results.render()[0]
    frame_queue.put(rendered_frame)

    command = get_command()
    if command:
        # Basic movements
        if "takeoff" in command:
            tello.takeoff()
        elif "land" in command:
            tello.land()
        elif "up" in command:
            tello.move_up(30)
        elif "down" in command:
            tello.move_down(30)
        elif "left" in command:
            tello.move_left(30)
        elif "right" in command:
            tello.move_right(30)
        elif "forward" in command:
            tello.move_forward(30)
        elif "back" in command:
            tello.move_back(30)
        elif "rotate left" in command or "counter clockwise" in command:
            tello.rotate_counter_clockwise(30)
        elif "rotate right" in command or "clockwise" in command:
            tello.rotate_clockwise(30)
        elif "stop" in command:
            break
        else:
            instruction = process_advanced_command(command)
            # You can then parse the 'instruction' for more nuanced commands or add more logic.

# Cleanup
frame_queue.put(None)
display_thread.join()
cv2.destroyAllWindows()
tello.land()
tello.end()
