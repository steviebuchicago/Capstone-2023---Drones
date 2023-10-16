import cv2
import torch

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Find the index for 'dog'
dog_index = model.names.index('dog')

# Start video capture from the computer's camera
cap = cv2.VideoCapture(1)

while True:
    # Get the current frame from the video capture
    ret, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Pass the frame to YOLOv5 for object detection
    results = model(frame_rgb)
    
    # Get labels of detected objects
    labels = results.pred[0][:, -1].int()

    # Check if a dog is detected in the frame
    if dog_index in labels:
        print("Dog detected!")

    # Convert results to rendered frame and display
    rendered_frame = results.render()[0]  # get the rendered frame
    cv2.imshow('YOLOv5', rendered_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
