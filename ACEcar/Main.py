import cv2
import pigpio
import keyboard
import threading
import time
import numpy as np
# print(cv2.getBuildInformation())

'''
pin config for final car

#Motor driver pins
INA- 5
INB- 6
Drive (PWM1)- 12
Steer (SPWM)- 13

#UART pins
UART TX- 14
UART RX- 15

#Other pins
ADC0,1:
    SPI- 7, 8, 9, 10, 11
    GPIO 7- CS1
    GPIO 8- CS0
Ultrasonic:
        Trig- 20
        Echo- 21
8x line IR- 16 
'''

steerPWM = 13
drivePWM = 12
INA = 5
INB = 6

# drive power (0-255)
Power = 25

########################MAIN##############################

def obav():
    global obx
    global oby
    obx =0
    oby =0

    # cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  # For live video
    cap = cv2.VideoCapture("C:/obs.avi")

    
    #obstacle color range
    low_b = np.uint8([5, 255, 255])
    high_b = np.uint8([0,14, 0])

    kernel = np.ones((5, 5), np.uint8) 
    while True:

        # read the frames and store them in the frame variable
        Ret, frame = cap.read()
        # cut off a part of the frame to not show too much
        frame = frame[150:330, 5:500]

        # find the contours of the line
        mask = cv2.inRange(frame, high_b, low_b)
        kernel = np.ones((5, 5), np.uint8)  # kernel for erosion and dilation
        mask = cv2.erode(mask, kernel, iterations=5)  # erode to remove noise
        # dilate to fill in the gaps
        mask = cv2.dilate(mask, kernel, iterations=9)
        # find the contours chenaged from NONE to SIMPLE can check the number between -1 and 1
        contours, hierachy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0: 

            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:

                obx = int(M['m10']/M['m00'])
                oby = int(M['m01']/M['m00'])
                # global value of cx

                # around 30 should be a sufficient vlaue to start driving backwards
                print(obx," ", oby)
                # make a cirlce at the center of the contour(x,y)
                cv2.circle(frame, (obx, oby), 5, (0, 0, 255), -1)

        # Draw the cotour of the line
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)
        # display the views
        cv2.imshow("Mask", mask)
        cv2.imshow("Frame", frame)
        # waits for q key to be pressed or for the CY value to be in range
        if cv2.waitKey(0) & 0xff == ord('q'):
            #or cy> 120 and cy < 130
            cap.release()
            cv2.destroyAllWindows()
            break

def main():
    global px
    global py
    px =0
    py =0

    # cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  # For live video
    cap = cv2.VideoCapture("C:/obs.avi")

    #line color ranges
    low_b = np.uint8([255, 255, 255]) 
    high_b = np.uint8([5, 5, 30])
    kernel = np.ones((5, 5), np.uint8)
    while True:

        # read the frames and store them in the frame variable
        Ret, frame = cap.read()
        # cut off a part of the frame to not show too much
        frame = frame[150:330, 5:500]

        # find the contours of the line
        mask = cv2.inRange(frame, high_b, low_b)
        kernel = np.ones((5, 5), np.uint8)  # kernel for erosion and dilation
        mask = cv2.erode(mask, kernel, iterations=5)  # erode to remove noise
        # dilate to fill in the gaps
        mask = cv2.dilate(mask, kernel, iterations=9)
        # find the contours chenaged from NONE to SIMPLE can check the number between -1 and 1
        contours, hierachy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:  # original was >0 changed for >255

            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:

                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                # global value of cx
                px = cx
                # 10 should be a sufficient vlaue to start driving backwards
                # gotta make sure the end condition isn't met before it's too late
                py = cy
                print(cx," ", cy)
                # make a cirlce at the center of the contour(x,y)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # Draw the cotour of the line
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)
        # display the views
        cv2.imshow("Mask", mask)
        cv2.imshow("Frame", frame)
        # waits for q key to be pressed or for the CY value to be in range
        if cv2.waitKey(0) & 0xff == ord('q') or cy> 120 and cy < 130:

            cap.release()
            cv2.destroyAllWindows()
            break


def camride():
    pi = pigpio.pi('acecar.local')
    #pi = pigpio.pi('raspberrypi.local')

    pi.set_mode(INA, pigpio.OUTPUT)
    pi.set_mode(INB, pigpio.OUTPUT)
    pi.set_mode(drivePWM, pigpio.OUTPUT)
    pi.set_mode(steerPWM, pigpio.OUTPUT)
    # Drive forward
    pi.set_PWM_dutycycle(drivePWM, Power)  # Power is PWM (from 0-255)
    pi.write(INA, 0)
    pi.write(INB, 1)
    while True:
        if keyboard.is_pressed('q'):
            pi.set_PWM_dutycycle(drivePWM, 0)
            pi.write(INA, 0)
            pi.write(INB, 0)
            pi.set_PWM_dutycycle(drivePWM, 0)
            pi.set_servo_pulsewidth(steerPWM, 1450)
            break

        if px < 50:
            print("CX: " + px + " L")
            pi.set_servo_pulsewidth(steerPWM, 1650)

        if pz> 50 and px < 300:
            print("CX: " + px + " C")
            pi.set_servo_pulsewidth(steerPWM, 1450)

        if px > 300:
            print("CX: " + px + " R")
            pi.set_servo_pulsewidth(steerPWM, 1150)


########Detection#######
#tmain = threading.Thread(target=main)
#tmain.start()

#######Control/Steering######
#tcamride = threading.Thread(target=camride)
#tcamride.start()

#######Obstacle avoidance#########
tobav = threading.Thread(target=obav)
tobav.start()


##Keyboard Control/testing####
#tcontrol = threading.Thread(target=control)
# tcontrol.start()
