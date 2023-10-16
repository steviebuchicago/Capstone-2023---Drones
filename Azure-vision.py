from djitellopy import Tello
import cv2 
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials 


# Azure Computer Vision setup
subscription_key = "d70108df80b1475b913e04527000db12"
endpoint = "https://comp-vision-steve-cv.cognitiveservices.azure.com/"
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Tello setup
tello = Tello('192.168.87.41')
tello.connect()
tello.streamon()

# Tracking variables 
bottle_found = False
bottle_pos = None
frame_num = 0

while True:

  # Get frame
  frame = tello.get_frame_read()
  img = frame.frame
  frame_num += 1

  # Analyze every 10 frames
  if frame_num % 10 == 0:
    analysis = computervision_client.analyze_image(img)

    if analysis.objects:
      for obj in analysis.objects:
        if obj.object_property == "Bottle":
          bottle_found = True
          bottle_pos = obj.rectangle
          break
      
    else:
      bottle_found = False

  # Track bottle
  if bottle_found:
    # Get bottle position
    x, y, w, h = bottle_pos
    
    # Center bottle in frame
    if x < img.shape[1]/3:
      tello.move_right(30) 
    elif x > 2*img.shape[1]/3:
      tello.move_left(30)

    # Forward/backward based on size 
    bottle_area = w * h
    if bottle_area > 3000:
      tello.move_backward(30)
    elif bottle_area < 2000:  
      tello.move_forward(30)

  # Annotate frame
  if analysis.objects:
    for obj in analysis.objects:
      x, y, w, h = obj.rectangle
      
      # Draw bounding box and label
      if obj.object_property == "Bottle":
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
        text = "Bottle"
        color = (0,255,0)  
      else:
        cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)
        text = obj.object_property
        color = (255,0,0)
        
      cv2.putText(img, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
  
  # Display frame rate
  cv2.putText(img, "FPS: " + str(frame_num), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2) 

  # Show output frame
  cv2.imshow("Detected Objects", img)
  cv2.waitKey(1)

  time.sleep(0.5)

# Clean up  
tello.land()
cv2.destroyAllWindows()