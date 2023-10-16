import cv2
import torch

# Load the YOLOv5 model and apply autoshape
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True).autoshape()

# Start video capture from the computer's camera
cap = cv2.VideoCapture(1)

while True:
    # Get the current frame from the video capture
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_tensor = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0)

    # Pass the frame to YOLOv5 for object detection
    results = model(frame_tensor)

    # Check if a dog is detected in the frame
    if 'dog' in results.names:
        print("Dog detected!")

    # Display the frame with bounding boxes
    results.render()  # updates results.imgs with boxes and labels
    for img in results.imgs:
        cv2.imshow('YOLOv5', img)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
