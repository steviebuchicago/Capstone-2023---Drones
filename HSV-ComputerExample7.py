import cv2
import numpy as np

# Define a function for the trackbar
def nothing(x):
    pass

# Open the webcam
cap = cv2.VideoCapture(0)

# Create a window for the trackbars
cv2.namedWindow("Trackbars")

# Create the trackbars for each HSV component
for i in ['MIN', 'MAX']:
    cv2.createTrackbar(f'H_{i}', "Trackbars", 0, 179, nothing)
    cv2.createTrackbar(f'S_{i}', "Trackbars", 0, 255, nothing)
    cv2.createTrackbar(f'V_{i}', "Trackbars", 0, 255, nothing)

# Set default value for MAX HSV trackbars.
cv2.setTrackbarPos('H_MAX', 'Trackbars', 179)
cv2.setTrackbarPos('S_MAX', 'Trackbars', 255)
cv2.setTrackbarPos('V_MAX', 'Trackbars', 255)

while True:
    # Read the frame from the camera
    ret, frame = cap.read()

    # Convert the frame from BGR to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get the current trackbar positions
    h_min = cv2.getTrackbarPos("H_MIN", "Trackbars")
    h_max = cv2.getTrackbarPos("H_MAX", "Trackbars")
    s_min = cv2.getTrackbarPos("S_MIN", "Trackbars")
    s_max = cv2.getTrackbarPos("S_MAX", "Trackbars")
    v_min = cv2.getTrackbarPos("V_MIN", "Trackbars")
    v_max = cv2.getTrackbarPos("V_MAX", "Trackbars")

    # Create a lower and upper threshold for the HSV range
    lower_threshold = np.array([h_min, s_min, v_min])
    upper_threshold = np.array([h_max, s_max, v_max])

    # Threshold the HSV image
    thresholded_image = cv2.inRange(hsv, lower_threshold, upper_threshold)

    # Show the thresholded image
    masked_image = cv2.bitwise_and(frame, frame, mask=thresholded_image)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding boxes on the masked image
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(masked_image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Convert the thresholded image to 3 channels
    thresholded_image_colored = cv2.cvtColor(thresholded_image, cv2.COLOR_GRAY2BGR)

    # Resize images for display
    frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    hsv = cv2.resize(hsv, (0, 0), fx=0.5, fy=0.5)
    thresholded_image_colored = cv2.resize(thresholded_image_colored, (0, 0), fx=0.5, fy=0.5)
    masked_image = cv2.resize(masked_image, (0, 0), fx=0.5, fy=0.5)

    # Combine images for display
    top = np.hstack((frame, hsv))
    bottom = np.hstack((thresholded_image_colored, masked_image))
    combined = np.vstack((top, bottom))

    # Show the combined image
    cv2.imshow("Combined Image", combined)

    # Exit if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and destroy all windows
cap.release()
cv2.destroyAllWindows()
