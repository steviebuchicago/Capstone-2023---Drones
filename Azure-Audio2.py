from djitellopy import Tello
import cv2
import azure.cognitiveservices.speech as speechsdk

def get_spoken_command():
    try:
        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {result.text}")  # Debugging line
            return result.text.lower()
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"Canceled: {cancellation.reason}")
            if cancellation.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation.error_details}")
    except Exception as e:
        print(f"Error in get_spoken_command: {e}")
    return None

tello = Tello('192.168.87.20')
print("Connecting to drone...")
tello.connect()
print("Connected to drone.")

speech_config = speechsdk.SpeechConfig(subscription='50a300bb2c854ceba19c8f2cb9dcd199', endpoint="https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language="en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

try:
    while True:
        command = get_spoken_command()

        if command:
            if "apple" in command:
                tello.takeoff()
                print("Drone taking off...")
            elif "banana" in command:
                tello.land()
                print("Drone landing...")
            elif "forward" in command:
                tello.move_forward(30)
                print("Drone moving forward...")
            elif "backward" in command:
                tello.move_backward(30)
                print("Drone moving backward...")
            elif "left" in command:
                tello.move_left(30)
                print("Drone moving left...")
            elif "right" in command:
                tello.move_right(30)
                print("Drone moving right...")
            elif "stop" in command or "halt" in command:
                tello.stop()
                print("Drone stopped.")

        frame = tello.get_frame_read().frame
        cv2.imshow("Tello Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tello.land()
    cv2.destroyAllWindows()
