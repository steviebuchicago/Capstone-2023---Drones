#FindSomethingLLM.py

#  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

#  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

#  speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")

import cv2
import torch
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
import openai

# Constants
TELLO_IP = '192.168.86.42'

# Setup YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

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

# OpenAI Setup
openai.api_key = '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'

def get_gpt3_response(prompt):
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=150)
    return response.choices[0].text.strip()

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

frame_read = tello.get_frame_read()
frame_skip = 10  # Adjust as needed
frame_counter = 0

while True:
    frame = frame_read.frame
    frame_counter += 1

    if frame_counter % frame_skip == 0:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(frame_rgb)
        rendered_frame = results.render()[0]
        # Directly show the frame here
        cv2.imshow('YOLOv5', rendered_frame)
        cv2.waitKey(1)

    command = get_command()

    if command:
        gpt3_response = get_gpt3_response(f"How should I move the drone when the command is: '{command}'?")
        
        if "up" in gpt3_response:
            tello.move_up(30)
        elif "down" in gpt3_response:
            tello.move_down(30)
        elif "left" in gpt3_response:
            tello.move_left(30)
        elif "right" in gpt3_response:
            tello.move_right(30)
        elif "forward" in gpt3_response:
            tello.move_forward(30)
        elif "back" in gpt3_response:
            tello.move_back(30)
        elif "takeoff" in gpt3_response:
            tello.takeoff()
        elif "land" in gpt3_response:
            tello.land()
        elif "stop" in gpt3_response:
            break
        else:
            # Handle any other directives or add more conditions as needed
            pass

# Cleanup
cv2.destroyAllWindows()
tello.land()
tello.end()
