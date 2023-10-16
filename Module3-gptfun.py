import openai
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
import os

# CONSTANTS
TELLO_IP = '192.168.87.52'

# DRONE Setup
tello = Tello(TELLO_IP)

# Initialize the OpenAI API (make sure to set up your API key)
openai.api_key = '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'

# COMMAND_ACTIONS Dictionary
KNOWN_COMMANDS = {
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


def get_dji_command(description):
    # Ask GPT to suggest a command based on the description
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Based on the description '{description}', the most appropriate DJI Tello drone command is:",
        max_tokens=100
    )
    
    suggested_command = response.choices[0].text.strip().lower()

    # Find the closest matching command from KNOWN_COMMANDS
    for cmd in KNOWN_COMMANDS:
        if cmd in suggested_command:
            return cmd

    return None  # If no known command is found

# Simulated interface
while True:
    description = input("Tell the drone what to do (or 'exit' to stop): ")
    
    if description.lower() == 'exit':
        break

    command = get_dji_command(description)
    
    if command:
        print(f"Suggested Command: {command}")
    else:
        print("Sorry, I couldn't determine an appropriate command.")
