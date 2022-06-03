import cv2
import pigpio
import keyboard
import threading
import time
import numpy as np
# print(cv2.getBuildInformatioqn())

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
Power = 20




########################MAIN##############################

tcap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  # For live video
ecap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')
ocap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')
#tcap = cv2.VideoCapture("C:/track.avi") #track detection video source
#ecap = cv2.VideoCapture("C:/track.avi") #end detection video source
#ocap = cv2.VideoCapture("C:/track.avi") #obstacle detection source


def obstacle_detection():
    global avoid
    avoid = False

    #obstacle color range
    low_b = np.uint8([5, 255, 255])
    high_b = np.uint8([0,5, 2])

    kernel = np.ones((5, 5), np.uint8) 
    while True:
        Ret, frame = ocap.read()
        # read the frames and store them in the frame variable
        # cut off a part of the frame to not show too much

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

                if oby > 200 and oby < 300:
                    avoid = True

                # around 30 should be a sufficient vlaue to start driving backwards
                print(obx," ", oby)
                # make a cirlce at the center of the contour(x,y)
                cv2.circle(frame, (obx, oby), 5, (0, 0, 255), -1)

        # Draw the cotour of the line
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)
        # display the views
        #cv2.imshow("ObstacleMask", mask)
        cv2.imshow("ObstacleFrame",frame)
        # waits for q key to be pressed or for the CY value to be in range
        cv2.waitKey(1)
        
def track_detection():
    global cx
    global area
    area = 0
    cx =0

    #cap = cv2.VideoCapture("C:/obs.avi")
    #line color ranges
    # high_b = np.uint8([255, 255, 255])
    # low_b = np.uint8([5, 5, 30]) #works pretty well with led

    high_b = np.uint8([255]) 
    low_b = np.uint8([8]) 
    
    #kernel = np.ones((6, 6), np.uint8)
    while True:

        # read the frames and store them in the frame variable
        Ret, frame = tcap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # cut off a part of the frame to not show too much
        frame = frame[0:360, 0:480]
        # find the contours of the line
        mask = cv2.inRange(frame[150:360, 0:480], low_b, high_b)
        kernel = np.ones((6, 6), np.uint8)  # kernel for erosion and dilation
        mask = cv2.erode(mask, kernel, iterations=5)  # erode to remove noise
        # dilate to fill in the gaps
        mask = cv2.dilate(mask, kernel, iterations=9)
        # find the contours chenaged from NONE to SIMPLE can check the number between -1 and 1
        contours, hierachy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:  # original was >0 changed for >255

            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            
            print((area := cv2.contourArea(c)))
            if M["m00"] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                #print(cx," ", cy)

                #make a cirlce at the center of the contour(x,y)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            

        # Draw the cotour of the line
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)
        # display the views
        cv2.imshow("TrackMast", mask)
        cv2.imshow("Outline", frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            ecap.release()
            ocap.release()
            time.sleep(0.5) # for some reason ecap has to close first or it wont exit cleanly
            cv2.destroyAllWindows()
            break
        
def control():
    pi = pigpio.pi('acecar.local')

    pi.set_mode(INA, pigpio.OUTPUT)
    pi.set_mode(INB, pigpio.OUTPUT)
    pi.set_mode(drivePWM, pigpio.OUTPUT)
    pi.set_mode(steerPWM, pigpio.OUTPUT)

    # Drive forward
    pi.set_PWM_dutycycle(drivePWM, Power)  # Power is PWM (from 0-255)
    pi.write(INA, 0)
    pi.write(INB, 1)
    while True:
        if keyboard.is_pressed('q') or area >= 54500.0 and area <= 60000.0:
            pi.set_servo_pulsewidth(steerPWM, 1450)
            pi.write(INA, 1)
            pi.write(INB, 0)
            pi.set_PWM_dutycycle(drivePWM, 40)
            time.sleep(0.2)
            pi.set_PWM_dutycycle(drivePWM, 0)
            pi.write(INA, 1)
            pi.write(INB, 0)
            ecap.release()
            tcap.release()
            ocap.release()
            time.sleep(0.5) # for some reason ecap has to close first or it wont exit cleanly
            cv2.destroyAllWindows()
            break
        
        
        if cx < 200:
            #print("CX: " + str(cx) + " L")
            pi.set_servo_pulsewidth(steerPWM, 1500)

        if cx> 200 and cx < 300:
            #print("CX: " + str(cx) + " C")
            pi.set_servo_pulsewidth(steerPWM, 1450)

        if cx > 300:
            #print("CX: " + str(cx) + " R")
            pi.set_servo_pulsewidth(steerPWM, 1100)

        '''if avoid == True:
            pi.set_servo_pulsewidth(steerPWM, 1450)
            pi.write(INA, 1)
            pi.write(INB, 0)
            time.sleep(3)
            pi.set_servo_pulsewidth(steerPWM, 1100)
            pi.write(INA, 0)    
            pi.write(INB, 1)
            time.sleep(1)
            pi.set_servo_pulsewidth(steerPWM, 1500)
            avoid = False'''
       

########Track detection#######
t_trackdetection = threading.Thread(target=track_detection)
t_trackdetection.start()

#########Obstacle detection#######
#t_obstacledetection = threading.Thread(target=obstacle_detection)
#t_obstacledetection.start()

#######Control/Steering######
t_control = threading.Thread(target=control)
t_control.start()