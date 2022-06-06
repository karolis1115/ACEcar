##########IMPORTS##########
import cv2
import time
import pigpio
import keyboard
import threading
import numpy as np


########OUTPUT PINS########

steerPWM = 13
drivePWM = 12
INA = 5
INB = 6


########MIN/MAX VALUES########

# Line following threshold
CX_MIN = 200
CX_MAX = 300

# Obstacle avoidance threshold
OBY_MIN = 200
OBY_MAX = 300

# Min/Max obstacle stop values
STOP_MIN = 54500.0
STOP_MAX = 60000.0


##########SERVO CONTROL##########

# Decrease for more RIGHT
SERVO_MIN = 1100

# Adjust for CENTER
SERVO_MID = 1450

# Increase for more LEFT
SERVO_MAX = 1500


#######POWER CONTROL########

# Drive power (0-255)
Power = 20


########################MAIN########################


#########VIDEO SOURCES#########

# tcap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  #For live video
# ocap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  #For live video
tcap = cv2.VideoCapture("C:/track.avi")  # Track detection video source
ocap = cv2.VideoCapture("C:/track.avi")  # Obstacle detection source


def obstacle_detection():

    # Global y axis value for obstacle detection
    global oby
    oby = 0

    # Obstacle color range
    low_b = np.uint8([5, 255, 255])
    high_b = np.uint8([0, 5, 2])

    while True:
        # Read the frames and store them in the frame variable
        Ret, frame = ocap.read()

        # Find the contours of the line
        mask = cv2.inRange(frame, high_b, low_b)

        kernel = np.ones((5, 5), np.uint8)  # Kernel for erosion and dilation
        mask = cv2.erode(mask, kernel, iterations=5)  # Erode to remove noise

        # Dilate to fill in the gaps
        mask = cv2.dilate(mask, kernel, iterations=9)

        # Find the contours chenaged from NONE to SIMPLE can check the number between -1 and 1
        contours, hierachy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:

            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:

                obx = int(M['m10']/M['m00'])
                oby = int(M['m01']/M['m00'])
                #print(obx, " ", oby)

                # Make a cirlce at the center of the contour(x,y)
                cv2.circle(frame, (obx, oby), 5, (0, 0, 255), -1)

        # Draw the cotour of the line
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)

        # Display the views
        #cv2.imshow("ObstacleMask", mask)
        cv2.imshow("ObstacleFrame", frame)

        # Stop the program if q key is pressed
        if cv2.waitKey(1) & keyboard.is_pressed('q'):
            ocap.release()
            cv2.destroyWindow("ObstacleFrame")
            break


def track_detection():

    # Center position in x axis (for track following)
    global cx
    cx = 0

    # Area of the contour (for end detection)
    global area
    area = 0

    # Track detection threashold
    high_b = np.uint8([255])
    low_b = np.uint8([8])

    while True:

        # Capture the frames and store them in the frame variable
        Ret, frame = tcap.read()

        # Convert the frames to gray scale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Cut off a part of the frame to not show too much
        frame = frame[0:360, 0:480]

        # Find the contours of the line
        mask = cv2.inRange(frame[150:360, 0:480], low_b, high_b)

        kernel = np.ones((6, 6), np.uint8)  # Kernel for erosion and dilation
        mask = cv2.erode(mask, kernel, iterations=5)  # Erode to remove noise

        # Dilate to fill in the gaps
        mask = cv2.dilate(mask, kernel, iterations=9)

        # Find the contours chenaged from NONE to SIMPLE can check the number between -1 and 1
        contours, hierachy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_SIMPLE)

        # If there is a contour do...
        if len(contours) > 0:

            # Find the biggest contour
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            print((area := cv2.contourArea(c)))

            # If the contour is big enough do...
            if M["m00"] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                #print(cx," ", cy)

                # Make a cirlce at the center of the contour(x,y)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # Draw the cotour of the line
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)

        # Display the views
        cv2.imshow("TrackMask", mask)
        cv2.imshow("Outline", frame)

        # Stop if q is pressed
        if cv2.waitKey(1) & keyboard.is_pressed('q'):
            ocap.release()
            cv2.destroyWindow("TrackMask")
            cv2.destroyWindow("Outline")
            break


def control():

    # Connect to remote gpio with this hostname
    pi = pigpio.pi('acecar.local')

    # Set the required pins to output
    pi.set_mode(INA, pigpio.OUTPUT)
    pi.set_mode(INB, pigpio.OUTPUT)
    pi.set_mode(drivePWM, pigpio.OUTPUT)
    pi.set_mode(steerPWM, pigpio.OUTPUT)

    # Drive forward
    pi.set_PWM_dutycycle(drivePWM, Power)  # Power is PWM (from 0-255)
    pi.write(INA, 0)
    pi.write(INB, 1)

    while True:

        #####################STEEERING##############################
        if cx < CX_MIN:
            #print("CX: " + str(cx) + " L")
            pi.set_servo_pulsewidth(steerPWM, SERVO_MAX)

        if cx > CX_MIN and cx < CX_MAX:
            #print("CX: " + str(cx) + " C")
            pi.set_servo_pulsewidth(steerPWM, SERVO_MID)

        if cx > CX_MAX:
            #print("CX: " + str(cx) + " R")
            pi.set_servo_pulsewidth(steerPWM, SERVO_MIN)

        #############OBSTACLE AVOIDANCE#############################
        if oby > OBY_MIN and oby < OBY_MAX:
            pi.set_servo_pulsewidth(steerPWM, SERVO_MID)

            # Drive backwards for 3 seconds
            pi.write(INA, 1)
            pi.write(INB, 0)
            time.sleep(3)

            # Turn right and drive forward for 3 seconds
            pi.set_servo_pulsewidth(steerPWM, SERVO_MIN)
            pi.write(INA, 0)
            pi.write(INB, 1)
            time.sleep(1)
            # Turn left and continue with program
            pi.set_servo_pulsewidth(steerPWM, SERVO_MAX)

        ###########################END EXECUTION##############################
        if keyboard.is_pressed('q') or area >= STOP_MIN and area <= STOP_MAX:

            # Center the wheels and drive backards at 40 pwm for 0.2 seconds
            pi.set_servo_pulsewidth(steerPWM, SERVO_MID)
            pi.write(INA, 1)
            pi.write(INB, 0)
            pi.set_PWM_dutycycle(drivePWM, 40)
            time.sleep(0.2)

            # Brake the car for 0.2 seconds
            pi.set_PWM_dutycycle(drivePWM, 255)
            pi.write(INA, 1)
            pi.write(INB, 1)
            time.sleep(0.2)

            # Set all outputs to 0
            pi.set_PWM_dutycycle(drivePWM, 0)
            pi.write(INA, 0)
            pi.write(INB, 0)
            pi.stop()
            break

#############################THREADS############################################


########TRACK DETECTION#######
t_trackdetection = threading.Thread(target=track_detection)
t_trackdetection.start()

#########OBSTACLE DETECTION#######
t_obstacledetection = threading.Thread(target=obstacle_detection)
t_obstacledetection.start()

#######CONTROL/STEERING######
t_control = threading.Thread(target=control)
t_control.start()
