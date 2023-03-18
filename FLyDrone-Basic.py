# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from djitellopy import Tello

# Connect to the drone using its IP address
drone1 = Tello('192.168.86.34')
#drone = Tello()
drone1.connect()

# Get Battery
drone1.get_battery()

# Take off
print(drone1.get_current_state())
drone1.takeoff()

# # Fly forward for 50cm
print(drone1.get_current_state())
drone1.set_speed(55)
drone1.move_forward(150)

# Fly left for 50cm
print(drone1.get_current_state())
drone1.rotate_clockwise(360)
drone1.move_left(50)

# # Fly back for 50cm
print(drone1.get_current_state())
drone1.flip_back()
drone1.move_back(165)


# Fly left for 50cm
print(drone1.get_current_state())
drone1.move_right(120)

# Land the drone
print(drone1.get_current_state())
drone1.land()
print(drone1.get_current_state())