from asyncio.windows_events import NULL
import cv2
import pigpio
import keyboard
import threading
import time
import numpy as np
# print(cv2.getBuildInformation())
steerPWM = 13
drivePWM = 12
driveDirrection = 5

pi = pigpio.pi('acecar.local')
pi.set_mode(driveDirrection, pigpio.OUTPUT)
pi.set_mode(drivePWM, pigpio.OUTPUT)


########################MAIN##############################


def video():
    cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')
    while True:
        # Opens capture source which is simply a url to the video stream
        frame = cap.read()
        if not frame:
            print("no valid frame")
            break
        # show the video output
        cv2.imshow("Output", frame)
        # waitkey has to be >0 to automatically update frame
        cv2.waitKey(5)
    cap.release()
    cv2.destroyAllWindows()


def control():
    while True:
        if keyboard.is_pressed('w'):
            pi.set_PWM_dutycycle(driveDirrection, 120)
            pi.write(drivePWM, 0)

        elif keyboard.is_pressed('s'):
            pi.write(driveDirrection, 0)
            pi.set_PWM_dutycycle(drivePWM, 120)

        elif keyboard.is_pressed('a'):
            pi.set_servo_pulsewidth(steerPWM, 1150)

        elif keyboard.is_pressed('d'):
            pi.set_servo_pulsewidth(steerPWM, 1550)

        else:
            #pi.set_servo_pulsewidth(steerPWM, 1350)
            pi.write(driveDirrection, 0)
            pi.write(drivePWM, 0)
            #pi.set_servo_pulsewidth(steerPWM, 0)


def main():
    global trg
    trg = 0

    cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  # For live video
    #cap.set(3, 160)
    #cap.set(4, 120)

    # Drive forward
    pi.set_PWM_dutycycle(driveDirrection, 100) # int is power (from 0-255)
    pi.write(drivePWM, 0) #when dirrection is set drive power is reversed 

    low_b = np.uint8([255, 255, 255])  # color of background
    high_b = np.uint8([80, 80, 150])

    while True:
        Ret, frame = cap.read()
        mask = cv2.inRange(frame, high_b, low_b)
        contours, hierachy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                trg = cx
                #print("CX: " + str(cx) + " CY:" + str(cy))
                
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)
        #cv2.imshow("Mask", mask)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xff == ord('q'):  # 1 is the time in ms
            cap.release()
            cv2.destroyAllWindows()
            pi.set_PWM_dutycycle(driveDirrection, 0)
            pi.set_servo_pulsewidth(steerPWM, 1350)
            break


def camride():
    while True:
        print(trg)
        if trg <= 340:
            #print("Turn Left")
            pi.set_servo_pulsewidth(steerPWM, 1150)

        if trg < 340 and trg > 300:
            #print("On track")
            pi.set_servo_pulsewidth(steerPWM, 1350)

        if trg >= 300:
            #print("Turn Right")
            pi.set_servo_pulsewidth(steerPWM, 1550)


tmain = threading.Thread(target=main)
tmain.start()

tcamride = threading.Thread(target=camride)
tcamride.start()

#tcontrol = threading.Thread(target=control)
#tcontrol.start()
#tvideo = threading.Thread(target=video)
#tvideo.start()
