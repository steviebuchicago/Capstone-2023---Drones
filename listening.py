from utlis import *
import cv2
w,h = 480,320
pid = [0.4,0.4,0]
pError = 0
startCounter = 0  # for no Flight 1   - for flight 0
 

#fly_drones_voice_3('192.168.86.25', '192.168.86.24')
#fly_drones_voice_2('192.168.86.25', '192.168.86.24')
#fly_drones('192.168.86.25', '192.168.86.24')
fly_drones_voice_3('192.168.86.24', '192.168.86.34')
