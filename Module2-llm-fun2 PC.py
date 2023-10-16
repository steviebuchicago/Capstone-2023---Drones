
import cv2
import torch
import openai
import azure.cognitiveservices.speech as speechsdk
import threading
import time

#########################
# SETUP
#########################

# Constants
YOLO_MODEL = 'ultralytics/yolov5s'
AZURE_SUBSCRIPTION_KEY = '55f2007ae13640a59b52e03dad3361ea'
AZURE_SERVICE_REGION = 'https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken'  # e.g., 'westus'
OPENAI_API_KEY = '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'

# Check CUDA availability
USE_CUDA = torch.cuda.is_available()
DEVICE = 'cuda:0' if USE_CUDA else 'cpu'

# Setup YOLOv5
print("Setting up YOLOv5...")
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True).to(DEVICE)
if USE_CUDA:
    model = model.half()  # Half precision improves FPS
print("YOLOv5 setup complete.")

# Setup Azure Speech SDK
print("Setting up Azure Speech SDK...")
# speech_config = speechsdk.SpeechConfig(subscription=AZURE_SUBSCRIPTION_KEY, region=AZURE_SERVICE_REGION)
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
print("Azure Speech SDK setup complete.")

# Setup OpenAI API
print("Setting up OpenAI...")
openai.api_key = OPENAI_API_KEY
print("OpenAI setup complete.")

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

#########################
# FUNCTIONS
#########################

def interpret_command_to_drone_action(command):
    for action_phrases, action in ACTIONS_TO_COMMANDS.items():
        if command in action_phrases:
            return action
    return None

def mock_execute_drone_command(command):
    print(f"Mock executed command: {command}")

def get_interpretation_from_openai(command):
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=f"What drone action corresponds to the command: '{command}'?",
        max_tokens=50
    )
    interpreted_action = response.choices[0].text.strip().lower()
    return interpret_command_to_drone_action(interpreted_action)

def listen_to_commands():
    print("Listening for commands. Speak into your microphone...")
    while True:
        print("Awaiting command...")
        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            command_heard = result.text.lower().strip('.')
            print(f"Heard: {command_heard}")
            
            drone_command = interpret_command_to_drone_action(command_heard)
            
            if not drone_command:
                drone_command = get_interpretation_from_openai(command_heard)
            
            if drone_command:
                mock_execute_drone_command(drone_command)
            else:
                print(f"Could not interpret the command: {command_heard}")

def start_video_feed():
    try:
        # Start the camera feed
        print("Attempting to start the camera feed...")
        
        # Try default camera first
        cap = cv2.VideoCapture(1)
        
        if not cap.isOpened():
            print("Default camera not accessible. Trying the next camera index...")
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("Second camera not accessible. Exiting.")
                return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # # Comment out YOLO processing for now to check basic video feed
            # cv2.imshow('Camera Feed', frame)
            
            # If YOLO processing is needed:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(frame_rgb)
            rendered_frame = results.render()[0]
            cv2.imshow('YOLOv5', rendered_frame)
            
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        print("Camera feed ended.")

    except Exception as e:
        print(f"Error starting the video feed: {e}")

#########################
# MAIN - Execute the program
#########################

if __name__ == "__main__":
    # Start listening for voice commands
    listen_to_commands_thread = threading.Thread(target=listen_to_commands)

    listen_to_commands_thread.start()
    time.sleep(5)  # Give a 5-second buffer before starting the video feed

    # Start the video feed sequentially to avoid overloading the system
    start_video_feed()

    listen_to_commands_thread.join()