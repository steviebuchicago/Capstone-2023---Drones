from djitellopy import Tello
import time
import speech_recognition as sr

# Create a Tello object
tello = Tello('172.20.10.14')

# Function to listen and recognize speech
def recognize_speech_from_mic(recognizer, microphone):
    # Check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")
    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # Adjust the recognizer sensitivity to ambient noise and record audio from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # Set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # Speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

# Create recognizer and microphone instances
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Try to connect to the drone
try:
    print("Connecting to drone...")
    tello.connect()
    print("Connected to drone!")
    print("Battery level: %s" % tello.get_battery())

    while True:
        print("Listening for commands. Say 'dog' to take off or 'banana' to land")
        command = recognize_speech_from_mic(recognizer, microphone)

        if command["transcription"]:
            print("You said: {}".format(command["transcription"]))
        else:
            print("I didn't catch that. What did you say?")
            continue

        # Execute the commands
        if command["transcription"].lower() == "dog":
            print("Taking off!")
            tello.takeoff()
            time.sleep(5)
        elif command["transcription"].lower() == "cat":
            print("Landing!")
            tello.land()
            time.sleep(5)
        else:
            print("Invalid command!")
except Exception as e:
    print(f"Failed to connect to the drone: {e}")
