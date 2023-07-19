from droneblocks.DroneBlocksTello import DroneBlocksTello
import time

tello = DroneBlocksTello()
tello.connect()
tello.set_top_led(r=255,g=0,b=0)
time.sleep(2)
tello.clear_display()
time.sleep(2)
tello.set_top_led(b=255,r=0,g=0)
tello.display_down_arrow()
tello.takeoff()
tello.display_sad()
time.sleep(2)
tello.clear_display()
time.sleep(2)
tello.display_heart()
time.sleep(2)
tello.move_up(20)
tello.rotate_counter_clockwise(90)
tello.display_smile()
tello.move_forward(100)
time.sleep(2)
tello.clear_display()
tello.land()

