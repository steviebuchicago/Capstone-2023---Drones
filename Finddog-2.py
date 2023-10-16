import cv2
import torch

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Get the dog index from model's class names
dog_index = model.names.index('dog')

# Start video capture from the computer's camera
cap = cv2.VideoCapture(1)

while True:
    # Get the current frame from the video capture
    ret, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Pass the frame to YOLOv5 for object detection
    results = model(frame_rgb)
    
    # Get labels and confidence scores of detected objects
    labels = results.pred[0][:, -1].int()
    confidences = results.pred[0][:, 4]

    # Check if a dog is detected in the frame
    if dog_index in labels:
        dog_detected_indices = [i for i, label in enumerate(labels) if label == dog_index]
        for idx in dog_detected_indices:
            confidence = confidences[idx].item() * 100
            print(f"Dog detected with confidence: {confidence:.2f}%!")
            
            # Draw confidence on the frame
            label_str = f"Dog: {confidence:.2f}%"
            box = results.pred[0][idx][:4].int()
            x1, y1, x2, y2 = box
            cv2.putText(frame, label_str, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Convert results to rendered frame and display
    rendered_frame = results.render()[0] # get the rendered frame
    cv2.imshow('YOLOv5', rendered_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
