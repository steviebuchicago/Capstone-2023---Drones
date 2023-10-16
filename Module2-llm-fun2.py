# Initialize the OpenAI API (make sure to set up your API key)
import cv2
import torch
import openai
import threading
import azure.cognitiveservices.speech as speechsdk

# SETUP OPENAI API
openai.api_key = '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'

# SETUP YOLOv5 FOR OBJECT DETECTION
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)

# SETUP WEBCAM
cap = cv2.VideoCapture(1)  # Default camera, usually webcam for PC

# AZURE SPEECH RECOGNITION SETUP
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language = "en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# ACTIONS TO COMMANDS MAPPING
ACTIONS_TO_COMMANDS = {
    ("start", "fly", "take off", "lift off"): "takeoff",
    ("land", "stop", "settle", "touch down"): "land",
    ("front flip", "forward flip", "tumble forward"): "flip",
    ("forward", "move ahead", "go straight"): "move_forward",
    ("backward", "move back", "retreat"): "move_back",
    ("left", "move left", "go leftward"): "move_left",
    ("right", "move right", "go rightward"): "move_right",
    ("up", "ascend", "rise"): "move_up",
    ("down", "descend", "lower"): "move_down",
    ("spin right", "rotate clockwise", "turn right"): "rotate_clockwise",
    ("spin left", "rotate counter-clockwise", "turn left"): "rotate_counter_clockwise",
    ("back flip", "flip back"): "flip_backward",
    ("right flip"): "flip_right",
    ("video on", "start video", "begin stream"): "streamon",
    ("video off", "stop video", "end stream"): "streamoff",
    ("go xyz", "specific move"): "go_xyz_speed"
}

command_queue = []

def listen_for_command():
    global command_queue
    while True:
        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            command_queue.append(result.text.lower())

def interpret_and_execute():
    global command_queue
    while True:
        if command_queue:
            command = command_queue.pop(0)  # Get the first command
            for keywords, action in ACTIONS_TO_COMMANDS.items():
                if any(keyword in command for keyword in keywords):
                    print(f"Mock executed command: {action}")
                    break

def detect_and_show_objects():
    while True:
        ret, frame = cap.read()  # Read a frame from the webcam
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Continuously detect objects
        detected_objects = model(frame_rgb)
        rendered_frame = detected_objects.render()[0]  # Visualization with bounding boxes
        cv2.imshow('YOLOv5', rendered_frame)
        cv2.waitKey(1)

# Start threads
threading.Thread(target=listen_for_command).start()
threading.Thread(target=interpret_and_execute).start()
threading.Thread(target=detect_and_show_objects).start()
