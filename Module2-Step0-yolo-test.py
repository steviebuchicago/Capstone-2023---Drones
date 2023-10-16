#test 

import cv2
import torch

# Setup YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Start video capture from the default computer's camera
cap = cv2.VideoCapture(0)

while True:
    # Get the current frame from the video capture
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Pass the frame to YOLOv5 for object detection
    results = model(frame_rgb)

    # Convert results to rendered frame and display
    rendered_frame = results.render()[0]
    cv2.imshow('YOLOv5', rendered_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
