import cv2
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import io

# Azure Computer Vision credentials
endpoint = "https://vision-adsp.cognitiveservices.azure.com/"
subscription_key = "1b13936cfaf64f9a95547c7f3839f5b7"

# Initialize the client
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def is_dog_detected(frame):
    # Convert the frame to a byte stream
    ret, buffer = cv2.imencode('.jpg', frame)
    stream = io.BytesIO(buffer)

    # Analyze the frame
    analysis = computervision_client.analyze_image_in_stream(
        stream,
        visual_features=[VisualFeatureTypes.objects]
    )

    # Check if there is a dog in the objects detected
    for detected_object in analysis.objects:
        if detected_object.object_property == "dog":
            return True
    return False

# Capture live feed
cap = cv2.VideoCapture(1)  # 0 for default camera

while True:
    ret, frame = cap.read()
    
    # You can skip a few frames if you want by using a counter or timer

    if is_dog_detected(frame):
        cv2.putText(frame, "Dog detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.imshow('Live Feed', frame)
    
    # Exit when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
