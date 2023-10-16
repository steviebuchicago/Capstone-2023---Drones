from djitellopy import Tello  
import cv2
import azure.cognitiveservices.speech as speechsdk

flying = False

def get_spoken_command():
  try:
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
      print(f"Recognized: {result.text}")
      return result.text.lower()
    
    # handle other reasons here

  except Exception as e:
    print(f"Error in get_spoken_command: {e}")
    
  return None

tello = Tello('192.168.87.46')
tello.connect()

speech_config = speechsdk.SpeechConfig(subscription='50a300bb2c854ceba19c8f2cb9dcd199', endpoint="https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language="en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

print("Say 'start' to begin.")

while True:

  command = get_spoken_command()
  
  if command == "start":
    break

print("Ready for commands...")

while True:

  print("Say a command...")
  
  command = get_spoken_command()

  if command == "apple" and not flying:
    print("Taking off...")
    flying = True
    tello.takeoff()

  elif command == "banana" and flying:
    print("Landing...")
    flying = False
    try:
      tello.land()
    except:
      print("Already landed")  

  elif command == "forward":
    print("Moving forward...")
    tello.move_forward(30)

  # add other move commands

  elif command == "stop":
    print("Stopping...")
    tello.stop()

  elif command == "end":
    break

  frame = tello.get_frame_read().frame
  cv2.imshow("Tello Feed", frame)

  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

  time.sleep(2)

print("Landing...")
tello.land()

tello.end()
cv2.destroyAllWindows()

print("Done.")