import cv2
import torch
import sys
import numpy as np

# Add the YOLOv5 directory to the Python path
sys.path.append("C:\\Users\\sbarr\\Downloads\\Summer-Drone-Capstone\\Capstone-2023---Drones\\yolov5")

from models.experimental import attempt_load

# Specify the path to your custom weights
weights_path = "C:\\Users\\sbarr\\Downloads\\Summer-Drone-Capstone\\Capstone-2023---Drones\\yolov5\\runs\\train\\steve_model7\\weights\\best.pt"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Load the YOLOv5 model with your custom weights
# model = attempt_load(weights_path, map_location=device).to(device).eval()
model = attempt_load(weights_path).to(device).eval()


# Start video capture from the default computer's camera
cap = cv2.VideoCapture(0)

while True:
    # Get the current frame from the video capture
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert frame to RGB and then to a tensor
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_tensor = torch.from_numpy(frame_rgb).float().permute(2,0,1).to(device) / 255.0
    frame_tensor = frame_tensor.unsqueeze(0)

    # Pass the tensor to YOLOv5 for object detection
    with torch.no_grad():
        predictions = model(frame_tensor)

    # Parse the predictions and draw bounding boxes
    boxes = predictions[0][0].cpu().numpy()
    for box in boxes:
        if box[4] > 0.5:  # confidence threshold
            c1 = tuple((box[0:2] * [frame.shape[1], frame.shape[0]]).astype(int))
            c2 = tuple((box[2:4] * [frame.shape[1], frame.shape[0]]).astype(int))
            cv2.rectangle(frame, c1, c2, (0, 255, 0), 2)
            label = f"Class: {int(box[5])}, Confidence: {box[4]:.2f}"
            cv2.putText(frame, label, (c1[0], c1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame with bounding boxes
    cv2.imshow('YOLOv5 Custom Model', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
