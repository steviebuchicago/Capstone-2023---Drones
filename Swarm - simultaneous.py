# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 00:41:15 2023

@author: sb5
"""

from djitellopy import Tello
import threading

# Connect to the first drone
drone1 = Tello('192.168.86.33')

# Connect to the second drone
drone2 = Tello('192.168.86.34')

#Connect both drones
drone1.connect()
drone2.connect()

# Create a thread for each drone's takeoff
thread1 = threading.Thread(target=drone1.takeoff)
thread2 = threading.Thread(target=drone2.takeoff)

# Start both threads
thread1.start()
thread2.start()

# Wait for both threads to complete
thread1.join()
thread2.join()

# Create a thread for each drone's takeoff
thread1 = threading.Thread(target=drone1.set_speed, args=(100,0))
thread2 = threading.Thread(target=drone2.set_speed, args=(100,0))

# Start both threads
thread1.start()
thread2.start()

# Wait for both threads to complete
thread1.join()
thread2.join()

# Create a thread for each drone's move forward
thread1 = threading.Thread(target=drone1.move_forward, args=(100,))
thread2 = threading.Thread(target=drone2.move_forward, args=(100,))

# Start both threads
thread1.start()
thread2.start()

# Wait for both threads to complete
thread1.join()
thread2.join()

# Create a thread for each drone's takeoff
thread1 = threading.Thread(target=drone1.flip_forward())
thread2 = threading.Thread(target=drone2.flip_forward())

# Start both threads
thread1.start()
thread2.start()

# Wait for both threads to complete
thread1.join()
thread2.join()

# Create a thread for each drone's takeoff
thread1 = threading.Thread(target=drone1.set_speed, args=(50,0))
thread2 = threading.Thread(target=drone2.set_speed, args=(50,0))

# Start both threads
thread1.start()
thread2.start()

# Wait for both threads to complete
thread1.join()
thread2.join()

# Create a thread for each drone's move forward
thread1 = threading.Thread(target=drone1.move_back, args=(100,))
thread2 = threading.Thread(target=drone2.move_back, args=(100,))

# Start both threads
thread1.start()
thread2.start()

# Wait for both threads to complete
thread1.join()
thread2.join()

# Create a thread for each drone's land
thread1 = threading.Thread(target=drone1.land)
thread2 = threading.Thread(target=drone2.land)

# Start both threads
thread1.start()
thread2.start()

# Wait for both threads to complete
thread1.join()
thread2.join()