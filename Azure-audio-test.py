import sounddevice as sd
import numpy as np
import azure.cognitiveservices.speech as speechsdk

# 1. List available microphones
def list_microphones():
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        print(f"ID: {idx}, Name: {device['name']}, Samplerate: {device['default_samplerate']}")

# 2. Record and playback audio for verification
def record_audio(device_id, duration=5):
    samplerate = int(sd.query_devices(device_id)['default_samplerate'])
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype='float64', device=device_id)
    print("Recording... Speak into the microphone.")
    sd.wait()
    print("Recording complete!")
    # Playback
    sd.play(recording, samplerate=samplerate)
    print("Playing back the recorded audio...")
    sd.wait()
    print("Playback complete!")
    return recording

# 3. Use Azure Speech SDK for speech recognition
def recognize_speech(device_name):
    speech_key, service_region = "50a300bb2c854ceba19c8f2cb9dcd199", "https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True, device_name=device_name)
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print("\nSay something for Azure Speech Recognition...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized:", result.text)
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print("Speech Recognition canceled:", cancellation.reason)
        if cancellation.reason == speechsdk.CancellationReason.Error:
            print("Error details:", cancellation.error_details)

if __name__ == "__main__":
    # Display available microphones
    list_microphones()
    mic_choice = input("\nEnter the ID of the microphone you want to test: ")
    device_name = sd.query_devices(int(mic_choice))['name']
    
    # Test chosen microphone
    record_audio(int(mic_choice))

    # Recognize speech using the chosen microphone
    recognize_speech(device_name)
