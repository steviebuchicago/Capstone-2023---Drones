from djitellopy import Tello
import cv2
import requests
import time

# Azure Computer Vision configurations
AZURE_ENDPOINT = "https://vision-adsp.cognitiveservices.azure.com/"
AZURE_KEY = "1b13936cfaf64f9a95547c7f3839f5b7"
AZURE_ANALYZE_URL = AZURE_ENDPOINT + "vision/v3.1/analyze"

HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_KEY,
    "Content-Type": "application/octet-stream"
}

PARAMS = {
    "visualFeatures": "Objects",
    "details": "Landmarks"
}

def analyze_image(img):
    """Send image to Azure Computer Vision for analysis."""
    ret, buffer = cv2.imencode('.jpg', img)
    response = requests.post(AZURE_ANALYZE_URL, headers=HEADERS, params=PARAMS, data=buffer.tobytes())
    data = response.json()
    return data

def find_dog_in_frame(data):
    """Check if a dog is present in the analysis results and return its bounding box."""
    objects = data.get('objects', [])
    for obj in objects:
        if obj['object'] == 'dog':
            return obj['rectangle']
    return None

def main():
    drone = Tello('192.168.87.46')
    drone.connect()
    drone.streamon()

    while True:
        frame = drone.get_frame_read().frame
        if frame is not None:
            data = analyze_image(frame)
            bbox = find_dog_in_frame(data)
            if bbox:
                # Draw bounding box around the dog
                top, left, width, height = bbox['y'], bbox['x'], bbox['w'], bbox['h']
                cv2.rectangle(frame, (left, top), (left+width, top+height), (0, 255, 0), 2)
                cv2.putText(frame, "Dog", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the frame
            cv2.imshow("Drone Feed", frame)
            key = cv2.waitKey(1) & 0xFF

            # If the 'q' key is pressed, break from the loop
            if key == ord('q'):
                break

        time.sleep(2)  # Wait for 2 seconds before analyzing the next frame

    cv2.destroyAllWindows()
    drone.streamoff()

if __name__ == "__main__":
    main()
