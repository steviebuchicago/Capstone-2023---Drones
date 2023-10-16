#findsomethingLLM-3.py

#  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
#  speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")

import cv2
import torch
import threading
import queue
import openai
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk

# Constants
TELLO_IP = '192.168.86.42'

# Setup YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)

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

# Initialize OpenAI
openai.api_key = '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'



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

# def interpret_command_with_openai(command):
#     """Interpret the voice command using OpenAI and return the drone action."""
#     response = openai.Completion.create(
#       engine="davinci",
#       prompt=f"I am a drone pilot and received the command '{command}'. What should I do?",
#       max_tokens=100
#     )
#     return response.choices[0].text.strip()

# def interpret_command_with_openai(command):
#     """Interpret the voice command using OpenAI and return the drone action."""
#     response = openai.Completion.create(
#       engine="davinci",
#       prompt=f"Translate the following drone command: '{command}'. What specific action should the drone perform?",
#       max_tokens=50
#     )
#     # Clean the response from unwanted patterns or characters
#     cleaned_response = response.choices[0].text.strip().replace('<br>', '').replace('::A:', '')
#     return cleaned_response

# frame_queue = queue.Queue(maxsize=5)
KNOWN_COMMANDS = [
    "curve_xyz_speed", "curve_xyz_speed_mid", "emergency", "end", "flip", "flip_back",
    "flip_forward", "flip_left", "flip_right", "get_acceleration_x", "get_acceleration_y",
    "get_acceleration_z", "get_barometer", "get_battery", "get_current_state", "get_distance_tof",
    "get_flight_time", "get_frame_read", "get_height", "get_highest_temperature", "get_lowest_temperature",
    "get_mission_pad_distance_x", "get_mission_pad_distance_y", "get_mission_pad_distance_z",
    "get_mission_pad_id", "get_own_udp_object", "get_pitch", "get_roll", "get_speed_x", "get_speed_y",
    "get_speed_z", "get_state_field", "get_temperature", "get_udp_video_address", "get_video_capture",
    "get_yaw", "go_xyz_speed", "go_xyz_speed_mid", "go_xyz_speed_yaw_mid", "land", "move", "move_back",
    "move_down", "move_forward", "move_left", "move_right", "move_up", "parse_state", "query_attitude",
    "query_barometer", "query_battery", "query_distance_tof", "query_flight_time", "query_height",
    "query_sdk_version", "query_serial_number", "query_speed", "query_temperature", "query_wifi_signal_noise_ratio",
    "raise_result_error", "rotate_clockwise", "rotate_counter_clockwise", "send_command_with_return",
    "send_command_without_return", "send_control_command", "send_rc_control", "send_read_command",
    "send_read_command_float", "send_read_command_int", "set_speed", "streamoff", "streamon", "takeoff"
]

def interpret_and_execute(command):
    """Interpret the voice command using OpenAI and execute the drone action."""
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"If someone instructs a DJI Tello drone to '{command}', which command from the following should the drone execute? {', '.join(KNOWN_COMMANDS)}",
        max_tokens=100
    )
    interpreted_command = response.choices[0].text.strip()

    # Based on the interpreted command, execute the drone function
    if interpreted_command == "takeoff":
        drone.takeoff()
    elif interpreted_command == "land":
        drone.land()
    elif interpreted_command == "flip":
        drone.flip("f")  # Default to forward flip. Adjust as needed.
    elif interpreted_command == "move_forward":
        drone.move_forward(20)  # Default to 20 cm. Adjust as needed.
    elif interpreted_command == "move_back":
        drone.move_back(20)
    elif interpreted_command == "move_left":
        drone.move_left(20)
    elif interpreted_command == "move_right":
        drone.move_right(20)
    elif interpreted_command == "move_up":
        drone.move_up(20)
    elif interpreted_command == "move_down":
        drone.move_down(20)
    elif interpreted_command == "rotate_clockwise":
        drone.rotate_clockwise(90)
    elif interpreted_command == "rotate_counter_clockwise":
        drone.rotate_counter_clockwise(90)

    # ... [Repeat for other commands, e.g.]
    
    elif interpreted_command == "streamon":
        drone.streamon()
    
    elif interpreted_command == "streamoff":
        drone.streamoff()

    # For commands that have required parameters, you will need to determine those values. Here's an example:
    elif interpreted_command == "go_xyz_speed":
        # These are default values. You'd probably want to determine these from the user's voice command.
        x, y, z, speed = 20, 20, 20, 10
        drone.go_xyz_speed(x, y, z, speed)

    # Continue in this manner for all commands...

    else:
        print(f"Unknown command: {interpreted_command}")

    return interpreted_command

# Example usage:
voice_command = "take off"  # This is what you get from your voice recognition system
command_to_execute = interpret_and_execute(voice_command)
print(f"Executing command: {command_to_execute}")

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

print("Voice command your drone! Start with 'takeoff' and control as you like.")
while True:
    frame = frame_read.frame
    frame_counter += 1

    if frame_counter % frame_skip == 0:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(frame_rgb)
        rendered_frame = results.render()[0]
        frame_queue.put(rendered_frame)

    command = get_command()
    if command:
        command = command.replace(".", "").strip()  # Clean up the command string

        # Basic drone controls
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
        elif "rotate left" in command:
            tello.rotate_counter_clockwise(30)
        elif "rotate right" in command:
            tello.rotate_clockwise(30)
        elif "stop" in command:
            break
        else:
            # For complex commands, get interpretation from OpenAI
            interpreted_command = interpret_command_with_openai(command)
            print(f"OpenAI Interpretation: {interpreted_command}")
            # Extend further based on what OpenAI might return. Example:
            if "inspect the ceiling" in interpreted_command:
                tello.move_up(50)
            elif "fly to the far corner" in interpreted_command:
                tello.move_forward(100)

frame_queue.put(None)
display_thread.join()
cv2.destroyAllWindows()
tello.land()
tello.end()
