from djitellopy import Tello
import torch
import cv2

# Connect to the drone
drone = Tello('192.168.87.46')
drone.connect()

# Check the drone's battery level
print(drone.get_battery())

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Start video streaming from the drone
drone.streamon()

while True:
    # Get the current frame from the drone's video stream
    frame_read = drone.get_frame_read()
    frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
    frame_tensor = torch.from_numpy(frame).unsqueeze(0)

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

# When everything is done, release the capture and stop the drone
drone.streamoff()
cv2.destroyAllWindows()