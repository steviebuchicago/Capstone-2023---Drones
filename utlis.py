from djitellopy import Tello
import cv2
import numpy as np
import concurrent.futures
import speech_recognition as sr


def fly_drones_voice_3(ip1, ip2):
    # Connect to the first drone
    drone1 = Tello(ip1)
    drone2 = Tello(ip2)
    # Connect both drones
    drone1.connect()
    drone2.connect()
    # Start streaming from both drones
    drone1.streamon()
    drone2.streamon()

    # Create recognizer
    r = sr.Recognizer()
    mic = sr.Microphone()

    #Take off Drone to start
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     take_off1 = executor.submit(drone1.takeoff)
    #     take_off2 = executor.submit(drone2.takeoff)
    # drone1.rotate_clockwise(360)
    # drone2.rotate_counter_clockwise(360)

    # Continuously listen for the oral command
    while True:
        with mic as source:
            audio = r.listen(source)
        try:
            command = r.recognize_google(audio).lower()
            if "end" in command:
                break
            elif "apple" in command:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    take_off1 = executor.submit(drone1.takeoff)
                    take_off2 = executor.submit(drone2.takeoff)
                    take_off1.result()
                    take_off2.result()
            elif "flip" in command:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    flip_forward1 = executor.submit(drone1.flip_forward)
                    flip_forward2 = executor.submit(drone2.flip_forward)
                    flip_forward1.result()
                    flip_forward2.result()
            elif "turtle" in command:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    flip_rotate1 = executor.submit(drone1.rotate_clockwise)
                    flip_rotate2 = executor.submit(drone2.rotate_counter_clockwise)
                    flip_rotate1.result(360)
                    flip_rotate2.result(360)
            elif "land" in command:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    take_land1 = executor.submit(drone1.land)
                    take_land2 = executor.submit(drone2.land)
                    take_land1.result()
                    take_land2.result()
        except sr.UnknownValueError:
            continue
        
    with concurrent.futures.ThreadPoolExecutor() as executor:
        land1 = executor.submit(drone1.land)
        land2 = executor.submit(drone2.land)
        land1.result()
        land2.result()


def fly_drones_voice(ip1, ip2):
    # Connect to the first drone
    drone1 = Tello(ip1)

    # Connect to the second drone
    drone2 = Tello(ip2)

    # Connect both drones
    drone1.connect()
    drone2.connect()

    # Start the video stream
    drone1.streamon()
    drone2.streamon()

    # Create a thread pool with 2 threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit commands to the thread pool
        takeoff1 = executor.submit(drone1.takeoff)
        takeoff2 = executor.submit(drone2.takeoff)

        # Wait for both commands to complete
        takeoff1.result()
        takeoff2.result()

        move_forward1 = executor.submit(drone1.move_forward, 50)
        move_forward2 = executor.submit(drone2.move_forward, 50)

        # Create a speech recognition object
        r1 = sr.Recognizer()
        r2 = sr.Recognizer()
        while True:
            # Listen for speech and print the result
            with sr.Microphone() as source:
                audio1 = r1.listen(source)
                audio2 = r2.listen(source)
                try:
                    # recognize speech using Google Speech Recognition
                    command1 = r1.recognize_google(audio1)
                    command2 = r2.recognize_google(audio2)
                    print("Drone 1 heard: " + command1)
                    print("Drone 2 heard: " + command2)
                    if command1.lower() == "land" or command2.lower() == "land":
                        break
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))

            # Get the video frame
            frame1 = drone1.get_frame_read().frame
            frame2 = drone2.get_frame_read().frame
            # Display the frame
            cv2.imshow("Drone 1", frame1)
            cv2.imshow("Drone 2", frame2)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        move_forward1.result()
        move_forward2.result()

        land1 = executor


def fly_drones_voice_2(ip1, ip2):
    # Connect to the first drone
    drone1 = Tello(ip1)
    drone2 = Tello(ip2)
    # Connect both drones
    drone1.connect()
    drone2.connect()
    # Start streaming from both drones
    drone1.streamon()
    drone2.streamon()

    # Create recognizer
    r = sr.Recognizer()
    mic = sr.Microphone()

    # Continuously listen for the oral command
    while True:
        with mic as source:
            audio = r.listen(source)
        try:
            command = r.recognize_google(audio).lower()
            if "land" in command:
                break
            elif "youtube" in command:
                drone1.takeoff()
                drone2.takeoff()
            elif "flip forward" in command:
                drone1.flip_forward()
                drone2.flip_forward()    
            elif "rotate" in command:
                drone1.rotate_clockwise(360)
                drone1.rotate_counterclockwise(360)
        except sr.UnknownValueError:
            continue
        
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Fly forward for 50cm
        move_forward1 = executor.submit(drone1.move_forward, 50)
        move_forward2 = executor.submit(drone2.move_forward, 50)
        move_forward1.result()
        move_forward2.result()
        # Wait for 5 seconds
        time.sleep(5)
    # Land the drones
    drone1.land()
    drone2.land()
    
    



def fly_drones(ip1, ip2):
    # Connect to the first drone
    drone1 = Tello(ip1)

    # Connect to the second drone
    drone2 = Tello(ip2)

    # Connect both drones
    drone1.connect()
    drone2.connect()

    # Create a thread pool with 2 threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit commands to the thread pool
        takeoff1 = executor.submit(drone1.takeoff)
        takeoff2 = executor.submit(drone2.takeoff)

        # Wait for both commands to complete
        takeoff1.result()
        takeoff2.result()

        move_forward1 = executor.submit(drone1.move_forward, 50)
        move_forward2 = executor.submit(drone2.move_forward, 50)

        # Create a speech recognition object
        r1 = sr.Recognizer()
        r2 = sr.Recognizer()
        # Listen for speech and print the result
        with sr.Microphone() as source:
            audio1 = r1.listen(source)
            audio2 = r2.listen(source)
            try:
                # recognize speech using Google Speech Recognition
                command1 = r1.recognize_google(audio1)
                command2 = r2.recognize_google(audio2)
                print("Drone 1 heard: " + command1)
                print("Drone 2 heard: " + command2)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

        move_forward1.result()
        move_forward2.result()

        land1 = executor.submit(drone1.land)
        land2 = executor.submit(drone2.land)
 
def initializeTello():
    myDrone = Tello('192.168.86.34')
    myDrone.connect()
    myDrone.for_back_velocity = 0
    myDrone. left_right_velocity = 0
    myDrone.up_down_velocity = 0
    myDrone.yaw_velocity = 0
    myDrone.speed = 0
    print(myDrone.get_battery())
    myDrone.streamoff()
    myDrone.streamon()
    return myDrone
 
def telloGetFrame(myDrone, w=480,h=320):
    myFrame = myDrone.get_frame_read()
    myFrame = myFrame.frame
    img = cv2.resize(myFrame,(w,h))
    return img
 
def findFace(img):
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray,1.1,6  )
 
    myFaceListC = []
    myFaceListArea = []
 
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        cx = x + w//2
        cy = y + h//2
        area = w*h
        myFaceListArea.append(area)
        myFaceListC.append([cx,cy])
 
    if len(myFaceListArea) !=0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i],myFaceListArea[i]]
    else:
        return img,[[0,0],0]
 
def trackFace(myDrone,info,w,pid,pError):
 
    ## PID
    error = info[0][0] - w//2
    speed = pid[0]*error + pid[1]*(error-pError)
    speed = int(np.clip(speed,-100,100))
 
 
    print(speed)
    if info[0][0] !=0:
        myDrone.yaw_velocity = speed
    else:
        myDrone.for_back_velocity = 0
        myDrone.left_right_velocity = 0
        myDrone.up_down_velocity = 0
        myDrone.yaw_velocity = 0
        error = 0
    if myDrone.send_rc_control:
        myDrone.send_rc_control(myDrone.left_right_velocity,
                                myDrone.for_back_velocity,
                                myDrone.up_down_velocity,
                                myDrone.yaw_velocity)
    return error
