#MobileNetV2

import cv2
import numpy as np
from djitellopy import Tello
import azure.cognitiveservices.speech as speechsdk
import time

# Initialize Tello Drone
tello = Tello('192.168.87.46')
tello.connect()

# Setup Azure Speech Recognition
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language = "en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

def get_command():
    try:
        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {result.text.lower()}")
            return result.text.lower()
    except Exception as e:
        print(f"Error in get_command: {e}")
    return None

# Load MobileNet SSD
net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "mobilenet_iter_73000.caffemodel")

# Load class names (COCO)
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Video capture
cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # set width
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # set height

print("Say 'start' to begin.")
while True:
    command = get_command()
    if command == "start.":
        print("Ready for commands...")
        break

print("Say the name of the object you want to detect:")
while True:
    object_to_detect = get_command().replace(".", "")
    if object_to_detect in classes:
        print(f"You have chosen to detect: {object_to_detect}")
        break
    else:
        print("Object not recognized. Please say the name of the object again:")

flying = False

while True:
    ret, frame = cap.read()
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.2:
            idx = int(detections[0, 0, i, 1])
            if classes[idx] == object_to_detect:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                label = "{}: {:.2f}%".format(classes[idx], confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Detection", frame)

    print("Say a command...")
    command = get_command()

    if command == "oscar." and not flying:
        print("Taking off...")
        flying = True
        tello.takeoff()
    elif command == "land." and flying:
        print("Landing...")
        flying = False
        tello.land()
    elif command == "apple.":
        print("Going forward...")
        tello.move_forward(100)
    elif command == "back.":
        print("Going back...")
        tello.move_back(100)
    elif command == "up.":
        print("Going up...")
        tello.move_up(30)
    elif command == "down.":
        print("Going down...")
        tello.move_down(30)
    elif command == "flip.":
        print("Flipping forward...")
        tello.flip_forward()
    elif command == "chip.":
        print("Flipping right...")
        tello.flip_right()
    elif command == "stop.":
        print("Stopping...")
        tello.stop()
    elif command == "end.":
        print("Ending...")
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
tello.land()
tello.end()
