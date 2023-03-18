from utlis import *
import cv2
w,h = 480,320
pid = [0.4,0.4,0]
pError = 0
startCounter = 0  # for no Flight 1   - for flight 0
 
 
myDrone = initializeTello()
while True:
 
    ## Flight
    if startCounter == 0:
        myDrone.takeoff()
        # myDrone.move_left(100)
        # myDrone.move_right(100)
        myDrone.move_up(60)
        myDrone.move_down(60)
        myDrone.rotate_clockwise(180)
        myDrone.rotate_counter_clockwise(180)
        #mydrone.flip_forward()
        #myDrone.rotate_clockwise(180)
        #myDrone.flip_forward()
  #   myDrone.flip_right()
        #myDrone.flip_back()
        # myDrone.flip()
        #myDrone.move_down(60)
        # myDrone.move_down(40)
        # myDrone.flip_backward()
        startCounter = 1
 
    ## Step 1
    img = telloGetFrame(myDrone,w,h)
    ## Step 2
    img, info = findFace(img)
    ## Step 3
    pError = trackFace(myDrone,info,w,pid,pError)
    print(info[0][0])
    cv2.imshow('Image',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #myDrone.land()
        break

# cap.release()
cv2.destroyAllWindows()