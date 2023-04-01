# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 10:58:47 2023

@author: sb5
"""
import cv2
import numpy as np

# Create a callback function for the trackbars
def on_trackbar(val):
    pass

# Create a named window for the trackbars and the thresholded image
cv2.namedWindow("Trackbars")
cv2.namedWindow("Thresholded Image")

# Create trackbars for adjusting the HSV range
cv2.createTrackbar("H_min", "Trackbars", 0, 179, on_trackbar)
cv2.createTrackbar("H_max", "Trackbars", 179, 179, on_trackbar)
cv2.createTrackbar("S_min", "Trackbars", 0, 255, on_trackbar)
cv2.createTrackbar("S_max", "Trackbars", 255, 255, on_trackbar)
cv2.createTrackbar("V_min", "Trackbars", 0, 255, on_trackbar)
cv2.createTrackbar("V_max", "Trackbars", 255, 255, on_trackbar)

# Open the default camera
cap = cv2.VideoCapture(0)

while True:
    # Read the frame from the camera
    ret, frame = cap.read()

    # Convert the frame from BGR to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get the current trackbar positions
    h_min = cv2.getTrackbarPos("H_min", "Trackbars")
    h_max = cv2.getTrackbarPos("H_max", "Trackbars")
    s_min = cv2.getTrackbarPos("S_min", "Trackbars")
    s_max = cv2.getTrackbarPos("S_max", "Trackbars")
    v_min = cv2.getTrackbarPos("V_min", "Trackbars")
    v_max = cv2.getTrackbarPos("V_max", "Trackbars")

    # Create a lower and upper threshold for the HSV range
    lower_threshold = np.array([h_min, s_min, v_min])
    upper_threshold = np.array([h_max, s_max, v_max])

    # Threshold the HSV image
    thresholded_image = cv2.inRange(hsv, lower_threshold, upper_threshold)

    # Show the thresholded image
    cv2.imshow("Thresholded Image", thresholded_image)

    # Show the original image with the threshold range applied
    masked_image = cv2.bitwise_and(frame, frame, mask=thresholded_image)
    cv2.imshow("Masked Image", masked_image)

    # Exit if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and destroy all windows
cap.release()
cv2.destroyAllWindows()
