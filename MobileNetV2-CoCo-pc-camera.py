import cv2
import azure.cognitiveservices.speech as speechsdk

# Load MobileNet SSD
net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "mobilenet_iter_73000.caffemodel")

# Load class names (COCO)
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Initialize Azure Speech Recognition
speech_config = speechsdk.SpeechConfig(subscription='55f2007ae13640a59b52e03dad3361ea', endpoint="https://northcentralus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language = "en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

def get_command():
    try:
        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {result.text.lower().strip('.')}")  # Dropping the period at the end
            return result.text.lower().strip('.')
    except Exception as e:
        print(f"Error in get_command: {e}")
    return None

# Prompt for object to detect
print("What object would you like to detect? (default: dog)")
object_to_detect = get_command() or "dog"
print(f"Did you say '{object_to_detect}'? If correct, say 'yes'. Otherwise, repeat the object.")

# Confirmation loop
while True:
    confirmation = get_command()
    if confirmation == "yes":
        break
    else:
        object_to_detect = confirmation
        print(f"Did you say '{object_to_detect}'? If correct, say 'yes'. Otherwise, repeat the object.")

# Set up video capture
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # set width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) # set height

while True:
    ret, frame = cap.read()

    # Forward pass the frame through the MobileNet SSD
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    # Loop over the detections
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.6:  # Confidence threshold
            idx = int(detections[0, 0, i, 1])
            label = classes[idx]
            if label == object_to_detect:
                box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                (startX, startY, endX, endY) = box.astype("int")
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                label = "{}: {:.2f}%".format(label, confidence * 100)
                cv2.putText(frame, label, (startX, startY-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("Frame", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
