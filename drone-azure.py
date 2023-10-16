from djitellopy import Tello
import cv2
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import azure.cognitiveservices.speech as speechsdk

# Initialization
tello = Tello('192.168.87.20')

#COG_SERVICE_ENDPOINT=https://steve-tst-1.cognitiveservices.azure.com/
#COG_SERVICE_KEY=df3e2acac2124cac9d093c4a1d0a885b

endpoint = "https://steve-tst-1.cognitiveservices.azure.com/"
key = "df3e2acac2124cac9d093c4a1d0a885b"
client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

# Azure Speech SDK Initialization
speech_key, service_region = "YOUR_AZURE_SPEECH_KEY", "YOUR_SERVICE_REGION"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

def get_spoken_command():
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text.lower()
    return None

try:
    while True:
        command = get_spoken_command()

        if "take off" in command:
            tello.takeoff()
        elif "land" in command:
            tello.land()
        # Add more voice commands if needed

        frame = tello.get_frame_read().frame
        cv2.imshow("Tello Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    tello.land()
    cv2.destroyAllWindows()
