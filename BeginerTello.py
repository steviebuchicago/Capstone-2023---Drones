# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 10:35:40 2023

@author: sb5
"""

from djitellopy import Tello
import time

def main():
    # Initialize the Tello drone
    tello = Tello()

    # Connect to the drone
    print("Connecting to drone...")
    tello.connect()
    print("Connected to drone.")

    # Check the battery level
    print(f"Current battery level: {tello.get_battery()}%")

    # Take off
    print("Taking off...")
    tello.takeoff()
    time.sleep(5)

    # Fly forward
    print("Flying forward...")
    tello.move_forward(100)
    time.sleep(5)


    # Fly forward
    print("Flying forward...")
    tello.move_up(100)

    # Fly forward
    print("Flying forward...")
    tello.flip_forward()
    tello.rotate_counter_clockwise(90)

    # Fly forward
    print("Flying forward...")
    tello.move_forward(100)
    time.sleep(5)


    # Land
    print("Landing...")
    tello.land()

if __name__ == "__main__":
    main()