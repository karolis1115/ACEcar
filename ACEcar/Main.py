from ast import While
import cv2
import pigpio
import keyboard
import threading
import time
import numpy as np
#print(cv2.getBuildInformation())


steerPWM =13
drivePWM =12
driveDirrection= 5

pi = pigpio.pi('acecar.local')
pi.set_mode(driveDirrection, pigpio.OUTPUT)
pi.set_mode(drivePWM, pigpio.OUTPUT)

########################MAIN##############################

def video():
    cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')
    while True:
        #Opens capture source which is simply a url to the video stream
        Ret,frame = cap.read()
        if not Ret:
            print("no valid frame")
            break
        #show the video output
        cv2.imshow("Output", frame)
        #waitkey has to be >0 to automatically update frame
        cv2.waitKey(5)
    cap.release()
    cv2.destroyAllWindows()

def control():
    while True: 
        if keyboard.is_pressed('w'):
            pi.set_PWM_dutycycle(driveDirrection,200)
            pi.write(drivePWM,0)
    
        elif keyboard.is_pressed('s'):
            pi.write(driveDirrection,0)
            pi.set_PWM_dutycycle(drivePWM,200)


        elif keyboard.is_pressed('a'):
            pi.set_servo_pulsewidth(steerPWM, 1200)

    
        elif keyboard.is_pressed('d'):
            pi.set_servo_pulsewidth(steerPWM, 1700)

        else:
            pi.set_servo_pulsewidth(steerPWM, 1450)
            pi.write(driveDirrection,0)
            pi.write(drivePWM,0)

tcontrol = threading.Thread(target=control)
tvideo = threading.Thread(target=video)
trecord = threading.Thread(target=record)
#tvideo.start()
tcontrol.start()
#trecord.start()

'''
Take video data -> detect line + obstacles + end -> follow line + avoid obstacles + stop at end
'''