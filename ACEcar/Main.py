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

'''
Take video data -> detect line + obstacles + end -> follow line + avoid obstacles + stop at end
'''

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


def main():

    #cap = cv2.VideoCapture('vid1.mp4')
    cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream') #For live video
    cap.set(3, 160)
    cap.set(4, 120)


    while True:
        #Drive forward
        pi.set_PWM_dutycycle(driveDirrection,200)
        pi.write(drivePWM,0)

        ret, frame = cap.read()

        low_b = np.uint8([255, 255, 255])  # color of background

        high_b = np.uint8([80, 80, 150])
        mask = cv2.inRange(frame, high_b, low_b)

        contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                print("CX: " + str(cx) + " CY:" + str(cy))
                if cx >= 1200:
                    print("Turn Left")
                    pi.set_servo_pulsewidth(steerPWM, 1200) #turn wheels left (probs needs adjusting)

                if cx < 1200 and cx > 1000:  # NEED TO CHANGE VALUES DEPENDS OF CAMERA
                    print("On track")
                    pi.set_servo_pulsewidth(steerPWM, 1450) ## center wheels (probs needs adjusting)

                if cx <= 1100:
                    print("Turn Right")
                    pi.set_servo_pulsewidth(steerPWM, 1700) #turn wheels right (probs needs adjusting)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)
        cv2.imshow("Mask", mask)
        cv2.imshow("Grame", frame)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xff == ord('q'):  # 1 is the time in ms
            break

    cap.release()
    cv2.destroyAllWindows()

tmain = threading.Thread(target=main)
tmain.start()
#tcontrol = threading.Thread(target=control)
#tvideo = threading.Thread(target=video)
#tvideo.start()
#tcontrol.start()