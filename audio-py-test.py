import sounddevice as sd

def list_microphones():
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        print(f"ID: {idx}, Name: {device['name']}, Samplerate: {device['default_samplerate']}")
        
list_microphones()