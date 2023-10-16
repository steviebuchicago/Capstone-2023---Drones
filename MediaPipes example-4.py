# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 15:19:53 2023

@author: sb5
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 19:06:08 2023
@author: sb5
"""

import cv2
import mediapipe as mp
import time
from djitellopy import Tello

# Initialize MediaPipe Hands and Tello drone
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
drone = Tello('192.168.87.56')

# Connect to the drone
drone.connect()
print(f"Battery: {drone.get_battery()}%")

# Connect to the drone's video stream
drone.streamon()

# Define gestures and drone commands
def detect_gesture(landmarks):
    thumbs_up = landmarks[mp_hands.HandLandmark.THUMB_TIP].y < landmarks[mp_hands.HandLandmark.THUMB_MCP].y
    thumbs_down = landmarks[mp_hands.HandLandmark.THUMB_TIP].y > landmarks[mp_hands.HandLandmark.THUMB_MCP].y

    middle_finger_up = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and \
                       landmarks[mp_hands.HandLandmark.THUMB_TIP].y > landmarks[mp_hands.HandLandmark.THUMB_MCP].y

    if thumbs_up:
        return "thumbs_up"
    elif thumbs_down:
        return "thumbs_down"
    elif middle_finger_up:
        return "middle_finger_up"
    else:
        return "none"

# Initialize the video capture
cap = cv2.VideoCapture('udp://192.168.87.56:11111')

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))

last_gesture_time = time.time()
in_air = False
frame_counter = 0
frames_to_skip = 60

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.4, min_tracking_confidence=0.4) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to get frame")
            break

        frame_counter += 1

        if frame_counter % frames_to_skip == 0:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (640, 480))

            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    if results.multi_handedness[0].classification[0].label == "Right":  # Only process the right hand
                        gesture = detect_gesture(hand_landmarks.landmark)
                        print(f"Detected gesture: {gesture}")

                        current_time = time.time()
                        if current_time - last_gesture_time > 5:
                            if gesture == "thumbs_up" and not in_air:
                                drone.takeoff()
                                last_gesture_time = current_time
                                in_air = True
                            elif gesture == "thumbs_down" and in_air:
                                drone.land()
                                last_gesture_time = current_time
                                in_air = False
                            elif gesture == "middle_finger_up" and in_air:
                                drone.flip_back()
                                last_gesture_time = current_time

                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # write the frame
            out.write(frame)

            # Display the resulting frame
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    # safely land the drone
    if in_air:
        drone.land()

    # end the video stream
    drone.streamoff()

    # release the video writer
    out.release()


