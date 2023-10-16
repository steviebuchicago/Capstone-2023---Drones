#findsomethingLLM-5.py

#  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
#  speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")



import cv2
import torch
import openai
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
import os

# CONSTANTS
TELLO_IP = '192.168.86.42'
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'dummy'  # Suppresses OpenCV warnings/errors related to frames

# SETUP OPENAI API
openai.api_key = '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'

# SETUP YOLOv5 FOR OBJECT DETECTION
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)

# TELLO DRONE SETUP
tello = Tello(TELLO_IP)
tello.connect()
tello.streamoff()
tello.streamon()
drone_state = 'landed'

# AZURE SPEECH RECOGNITION SETUP
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language = "en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# COMMAND_ACTIONS Dictionary
COMMAND_ACTIONS = {
    "takeoff": (tello.takeoff, []),
    "land": (tello.land, []),
    "flip": (tello.flip, ["f"]),
    "move_forward": (tello.move_forward, [20]),
    "move_back": (tello.move_back, [20]),
    "move_left": (tello.move_left, [20]),
    "move_right": (tello.move_right, [20]),
    "move_up": (tello.move_up, [20]),
    "move_down": (tello.move_down, [20]),
    "rotate_clockwise": (tello.rotate_clockwise, [90]),
    "rotate_counter_clockwise": (tello.rotate_counter_clockwise, [90]),
    "flip_backward": (tello.flip, ['b']),
    "flip_right": (tello.flip, ['r']),
    "streamon": (tello.streamon, []),
    "streamoff": (tello.streamoff, []),
    "go_xyz_speed": (tello.go_xyz_speed, [20, 20, 20, 10]) # x, y, z, speed = 20, 20, 20, 10
    # ... Add more as needed
}


def get_command():
    """Listen for a voice command using Azure's Speech SDK and return the recognized text."""
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

def interpret_and_execute(command):
    """Interpret the voice command using OpenAI and execute the drone action."""
    global drone_state
    
    # Multi-shot prompt with examples
    prompt = f"What is the corresponding DJI Tello drone command for the voice command '{command}'?"

    # prompt = (
    #     "Translate the following voice commands into DJI Tello drone commands:\n"
    #     "Voice: 'take off' -> Drone: 'takeoff'\n"
    #     "Voice: 'land' -> Drone: 'land'\n"
    #     "Voice: 'flip' -> Drone: 'flip'\n"
    #     "Voice: 'go up' -> Drone: 'up'\n"
    #     "Voice: 'right flip' -> Drone: 'flip_right'\n"
    #     "Voice: 'dance' -> Drone: 'flip_backward'\n"
    #     "Voice: 'rise up' -> Drone: 'up'\n"
    #     "Voice: 'go down' -> Drone: 'down'\n"
    #     "Voice: 'turn left quickly' -> Drone: 'left'\n"
    #     "Voice: 'move forward' -> Drone: 'forward'\n"
    #     "...\n"
    #     f"Voice: '{command}' -> Drone: "
    # )
    
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=10  # Limit to 10 tokens to get a concise answer
    )
    print(f"OpenAI Response: {response.choices[0].text.strip()}")
    response_command = response.choices[0].text.strip()

    if drone_state == 'landed' and response_command != 'takeoff':
        print("Drone is not flying. Use 'takeoff' command first.")
        return None
    elif drone_state == 'flying' and response_command == 'takeoff':
        print("Drone is already flying. Use another command or 'land' to land.")
        return None

    if response_command == 'takeoff':
        drone_state = 'flying'
    elif response_command == 'land':
        drone_state = 'landed'

    return response_command if response_command in COMMAND_ACTIONS else None

    return response_command if response_command in COMMAND_ACTIONS else None

def execute_drone_command(command):
    """Execute a specific drone command based on its string representation."""
    func, args = COMMAND_ACTIONS.get(command, (None, None))
    if func:
        func(*args)
        print(f"Executed command: {command}")
    else:
        print(f"Unknown command: {command}")

# MAIN LOOP
print("Voice command your drone! Start with 'takeoff' and control as you like.")
while True:
    frame_read = tello.get_frame_read()
    frame = frame_read.frame
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(frame_rgb)
    rendered_frame = results.render()[0]
    cv2.imshow('YOLOv5', rendered_frame)
    cv2.waitKey(1)

    command = get_command()
    if command:
        command = command.replace(".", "").strip()
        interpreted_command = interpret_and_execute(command)
        if interpreted_command:
            execute_drone_command(interpreted_command)
        else:
            print(f"Unknown command: {interpreted_command}")
            print("Please repeat or try another command.")

cv2.destroyAllWindows()
tello.land()
tello.end()
