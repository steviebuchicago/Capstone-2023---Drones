from djitellopy import Tello
import cv2
import azure.cognitiveservices.speech as speechsdk

# Tello Drone Initialization
# tello = Tello()

# # Azure Speech SDK Initialization
# speech_key, service_region = "YOUR_AZURE_SPEECH_KEY", "YOUR_SERVICE_REGION"
tello = Tello('192.168.87.20')

# Connect to the drone
print("Connecting to drone...")
tello.connect()
print("Connected to drone.")
    
#COG_SERVICE_ENDPOINT=https://steve-tst-1.cognitiveservices.azure.com/
#COG_SERVICE_KEY=df3e2acac2124cac9d093c4a1d0a885b
# speech_config = speechsdk.SpeechConfig(subscription='df3e2acac2124cac9d093c4a1d0a885b', endpoint="https://steve-tst-1.cognitiveservices.azure.com/sts/v1.0/issuetoken")

speech_config = speechsdk.SpeechConfig(subscription='50a300bb2c854ceba19c8f2cb9dcd199', endpoint="https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language="en-US"

# audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
# tello.takeoff()

# Function to obtain the voice command
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

try:
    while True:
        command = get_spoken_command()

        if command:
            if "apple" in command:
                tello.takeoff()
            elif "banana" in command:
                tello.land()
            # Add more voice commands if needed

        frame = tello.get_frame_read().frame
        cv2.imshow("Tello Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tello.land()
    cv2.destroyAllWindows()
