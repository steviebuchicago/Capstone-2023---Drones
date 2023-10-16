#findsomethingLLM-3.py

#  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
#  speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")


import cv2
import torch
import openai
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
import os
drone_state = 'landed'  # Or any default state

# --- CONSTANTS ---
TELLO_IP = '192.168.86.42'
# KNOWN_COMMANDS = [
#     "curve_xyz_speed", "curve_xyz_speed_mid", "emergency", "end", "flip", "flip_back",
#     "flip_forward", "flip_left", "flip_right", "get_acceleration_x", "get_acceleration_y",
#     "get_acceleration_z", "get_barometer", "get_battery", "get_current_state", "get_distance_tof",
#     "get_flight_time", "get_frame_read", "get_height", "get_highest_temperature", "get_lowest_temperature",
#     "get_mission_pad_distance_x", "get_mission_pad_distance_y", "get_mission_pad_distance_z",
#     "get_mission_pad_id", "get_own_udp_object", "get_pitch", "get_roll", "get_speed_x", "get_speed_y",
#     "get_speed_z", "get_state_field", "get_temperature", "get_udp_video_address", "get_video_capture",
#     "get_yaw", "go_xyz_speed", "go_xyz_speed_mid", "go_xyz_speed_yaw_mid", "land", "move", "move_back",
#     "move_down", "move_forward", "move_left", "move_right", "move_up", "parse_state", "query_attitude",
#     "query_barometer", "query_battery", "query_distance_tof", "query_flight_time", "query_height",
#     "query_sdk_version", "query_serial_number", "query_speed", "query_temperature", "query_wifi_signal_noise_ratio",
#     "raise_result_error", "rotate_clockwise", "rotate_counter_clockwise", "send_command_with_return",
#     "send_command_without_return", "send_control_command", "send_rc_control", "send_read_command",
#     "send_read_command_float", "send_read_command_int", "set_speed", "streamoff", "streamon", "takeoff"
# ]

# ... [all the imports and setup code above]

# Replace the KNOWN_COMMANDS list with the COMMAND_ACTIONS dictionary
COMMAND_ACTIONS = {
    "takeoff": (tello.takeoff, []),
    "land": (tello.land, []),
    "flip": (tello.flip, ["f"]),
    "move_forward": (tello.move_forward, [20]),
    # ... add more as needed
}

# ... [keep all the other function definitions]

os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'dummy'  # Suppresses OpenCV warnings/errors related to frames

# --- SETUP OPENAI API ---
openai.api_key = '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'

# --- SETUP YOLOv5 FOR OBJECT DETECTION ---
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)

# --- TELLO DRONE SETUP ---
TELLO_IP = '192.168.86.42'
tello = Tello(TELLO_IP)
tello.connect()
tello.streamoff()
tello.streamon()
in_flight = False

# Assuming you initialize drone_state as 'landed' or 'flying' elsewhere in your script
drone_state = 'landed'

# --- AZURE SPEECH RECOGNITION SETUP ---
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language = "en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# --- FUNCTIONS ---

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
    prompt = (
        "Translate the following voice commands into DJI Tello drone commands:\n"
        "Voice: 'take off' -> Drone: 'takeoff'\n"
        "Voice: 'land' -> Drone: 'land'\n"
        "Voice: 'flip' -> Drone: 'flip'\n"
        "Voice: 'go up' -> Drone: 'up'\n"
        "Voice: 'right flip' -> Drone: 'flip_right'\n"
        "Voice: 'dance' -> Drone: 'flip_backward'\n"
        "Voice: 'rise up' -> Drone: 'up'\n"
        "Voice: 'go down' -> Drone: 'down'\n"
        "Voice: 'turn left quickly' -> Drone: 'left'\n"
        "Voice: 'move forward' -> Drone: 'forward'\n"
        "...\n"
        f"Voice: '{command}' -> Drone: "
    )

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50  # Limit to 50 tokens to get a concise answer
    )

    # Debug print
    print(f"OpenAI Response: {response.choices[0].text.strip()}")

    # Extract the command from the response
    response_command = response.choices[0].text.strip().split(':')[-1].strip()

    # Validate the command based on the drone's state
    if drone_state == 'landed' and response_command != 'takeoff':
        print("Drone is not flying. Use 'takeoff' command first.")
        return None
    elif drone_state == 'flying' and response_command == 'takeoff':
        print("Drone is already flying. Use another command or 'land' to land.")
        return None

    # If command is 'takeoff' or 'land', update the drone state
    if response_command == 'takeoff':
        drone_state = 'flying'
    elif response_command == 'land':
        drone_state = 'landed'

    # Check if the extracted command is in the known commands
    if response_command in KNOWN_COMMANDS:
        return response_command
    else:
        return None


def execute_drone_command(command):
    """Execute a specific drone command based on its string representation."""
    if command == "takeoff":
        tello.takeoff()
    elif command == "land":
        tello.land()
    elif command == "flip":
        tello.flip("f")  # Default to forward flip. Adjust as needed.
    elif command == "move_forward":
        tello.move_forward(20)  # Default to 20 cm. Adjust as needed.
    elif command == "move_back":
        tello.move_back(20)
    elif command == "move_left":
        tello.move_left(20)
    elif command == "move_right":
        tello.move_right(20)
    elif command == "move_up":
        tello.move_up(20)
    elif command == "move_down":
        tello.move_down(20)
    elif command == "rotate_clockwise":
        tello.rotate_clockwise(90)
    elif command == "rotate_counter_clockwise":
        tello.rotate_counter_clockwise(90)
    elif command == "flip_backward":
        tello.flip('b')
    elif command == "flip_right":
        tello.flip('r')
    elif command == "streamon":
        tello.streamon()
    elif command == "streamoff":
        tello.streamoff()
    elif command == "go_xyz_speed":
        x, y, z, speed = 20, 20, 20, 10
        tello.go_xyz_speed(x, y, z, speed)
    else:
        print(f"Unknown command: {command}")

    return command

# --- MAIN LOOP ---

print("Voice command your drone! Start with 'takeoff' and control as you like.")
while True:
    # Fetch and display frames from the drone's video stream
    frame_read = tello.get_frame_read()
    frame = frame_read.frame
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(frame_rgb)
    rendered_frame = results.render()[0]
    cv2.imshow('YOLOv5', rendered_frame)
    cv2.waitKey(1)

    # Listen for voice commands
    command = get_command()
    if command:
        command = command.replace(".", "").strip()  # Clean up the command string

        # Interpret and execute command
        interpreted_command = interpret_and_execute(command)

        if interpreted_command:
            drone_function = COMMAND_ACTIONS.get(interpreted_command)
            if drone_function:
                drone_function()
                print(f"Executed command: {interpreted_command}")
        else:
            print(f"Unknown command: {interpreted_command}")
            print("Please repeat or try another command.")

cv2.destroyAllWindows()
tello.land()
tello.end()
