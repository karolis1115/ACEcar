import cv2
import time
import pigpio
import keyboard
import threading
import numpy as np


#####OUTPUT PINS######

steerPWM = 13
drivePWM = 12
INA = 5
INB = 6


######MIN/MAX VALUES######

# Line following threshold
CX_MIN = 200
CX_MAX = 300

# Obstacle avoidance threshold
OBY_MIN = 200
OBY_MAX = 300

# Min/Max obstacle stop values
STOP_MIN = 54500.0
STOP_MAX = 60000.0


####SERVO CONTROL#####

# Decrease for more RIGHT
SERVO_MIN = 1100

# Adjust for CENTER
SERVO_MID = 1450

# Increase for more LEFT
SERVO_MAX = 1500


####POWER CONTROL#####
# drive power (0-255)
Power = 20


########################MAIN##############################


#########SOURCES#############

# tcap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  #For live video
# ocap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  #For live video
tcap = cv2.VideoCapture("C:/track.avi")  # track detection video source
ocap = cv2.VideoCapture("C:/track.avi")  # obstacle detection source


def obstacle_detection():

    # global y axis value for obstacle detection
    global oby
    oby = 0

    # obstacle color range
    low_b = np.uint8([5, 255, 255])
    high_b = np.uint8([0, 5, 2])

    kernel = np.ones((5, 5), np.uint8)
    while True:
        # read the frames and store them in the frame variable
        Ret, frame = ocap.read()

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
                #print(obx, " ", oby)

                # make a cirlce at the center of the contour(x,y)
                cv2.circle(frame, (obx, oby), 5, (0, 0, 255), -1)

        # Draw the cotour of the line
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)

        # display the views
        #cv2.imshow("ObstacleMask", mask)
        cv2.imshow("ObstacleFrame", frame)

        # stop the program if q key is pressed
        if cv2.waitKey(1) & keyboard.is_pressed('q'):
            ocap.release()
            cv2.destroyWindow("ObstacleFrame")
            break


def track_detection():

    # center position in x axis (for track following)
    global cx

    # area of the contour (for end detection)
    global area
    area = 0
    cx = 0

    # track color range
    high_b = np.uint8([255])
    low_b = np.uint8([8])

    while True:

        # capture the frames and store them in the frame variable
        Ret, frame = tcap.read()

        # Convert the frames to gray scale
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

        # if there is a contour do...
        if len(contours) > 0:

            # find the biggest contour
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            print((area := cv2.contourArea(c)))

            # if the contour is big enough do...
            if M["m00"] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                #print(cx," ", cy)

                # make a cirlce at the center of the contour(x,y)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # Draw the cotour of the line
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)

        # display the views
        cv2.imshow("TrackMask", mask)
        cv2.imshow("Outline", frame)

        # stop if q is pressed
        if cv2.waitKey(1) & keyboard.is_pressed('q'):
            ocap.release()
            cv2.destroyWindow("TrackMask")
            cv2.destroyWindow("Outline")
            break


def control():

    # connect to remote gpio with this hostname
    pi = pigpio.pi('acecar.local')

    # set the required pins to output
    pi.set_mode(INA, pigpio.OUTPUT)
    pi.set_mode(INB, pigpio.OUTPUT)
    pi.set_mode(drivePWM, pigpio.OUTPUT)
    pi.set_mode(steerPWM, pigpio.OUTPUT)

    # Drive forward
    pi.set_PWM_dutycycle(drivePWM, Power)  # Power is PWM (from 0-255)
    pi.write(INA, 0)
    pi.write(INB, 1)

    while True:

        if cx < CX_MIN:
            #print("CX: " + str(cx) + " L")
            pi.set_servo_pulsewidth(steerPWM, SERVO_MAX)

        if cx > CX_MIN and cx < CX_MAX:
            #print("CX: " + str(cx) + " C")
            pi.set_servo_pulsewidth(steerPWM, SERVO_MID)

        if cx > CX_MAX:
            #print("CX: " + str(cx) + " R")
            pi.set_servo_pulsewidth(steerPWM, SERVO_MIN)

        # obstacle avoidance task
        if oby > 200 and oby < 300:
            pi.set_servo_pulsewidth(steerPWM, SERVO_MID)
            pi.write(INA, 1)
            pi.write(INB, 0)
            time.sleep(3)
            pi.set_servo_pulsewidth(steerPWM, SERVO_MIN)
            pi.write(INA, 0)
            pi.write(INB, 1)
            time.sleep(1)
            pi.set_servo_pulsewidth(steerPWM, SERVO_MAX)

        # Stop if q is pressed or if the "area" variable is inside the range
        if keyboard.is_pressed('q') or area >= STOP_MIN and area <= STOP_MAX:

            # Center the wheels and drive backards at 40 pwm for 0.2 seconds
            pi.set_servo_pulsewidth(steerPWM, SERVO_MID)
            pi.write(INA, 1)
            pi.write(INB, 0)
            pi.set_PWM_dutycycle(drivePWM, 40)
            time.sleep(0.2)

            # brake the car for 0.2 seconds
            pi.set_PWM_dutycycle(drivePWM, 255)
            pi.write(INA, 1)
            pi.write(INB, 1)
            time.sleep(0.2)

            # set all outputs to 0
            pi.set_PWM_dutycycle(drivePWM, 0)
            pi.write(INA, 0)
            pi.write(INB, 0)
            pi.stop()
            break

#############################THREADS############################################


########Track detection#######
t_trackdetection = threading.Thread(target=track_detection)
t_trackdetection.start()

#########Obstacle detection#######
t_obstacledetection = threading.Thread(target=obstacle_detection)
t_obstacledetection.start()

#######Control/Steering######
t_control = threading.Thread(target=control)
# t_control.start()
