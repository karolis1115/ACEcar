##########IMPORTS##########
import cv2
import time
import pigpio
import keyboard
import threading
import numpy as np


########OUTPUT PINS########

ServoPin = 13
MotorPin = 12
INA = 5
INB = 6


########MIN/MAX VALUES########

# Line following threshold
CX_MIN = 200
CX_MAX = 300


# Min/Max obstacle stop values
STOP_MIN = 54500.0
STOP_MAX = 60000.0


##########SERVO CONTROL##########

# Decrease for more RIGHT
SERVO_MIN = 1380

# Adjust for CENTER
SERVO_MID = 1430

# Increase for more LEFT
SERVO_MAX = 1470

#######POWER CONTROL########

# Drive power (0-255)
Power = 255




#########VIDEO SOURCES#########

#tcap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  #For live video
tcap = cv2.VideoCapture("C:/track.avi")  # Track detection video source


def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def track_detection():

    # Center position in x axis (for track following)
    global cx
    cx = 0

    # Area of the contour (for end detection)
    global area
    area = 0

    # Track detection threashold
    high_b = np.uint8([255])
    low_b = np.uint8([100])

    while True:

        # Capture the frames and store them in the frame variable
        Ret, frame = tcap.read()

        # Convert the frames to gray scale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Cut off a part of the frame to not show too much
        frame = frame[0:360, 0:480]
        frame = cv2.blur(frame, (1, 100)) # Blur the image to remove noise

        mask = cv2.inRange(frame, low_b, high_b)

        kernel = np.ones((6, 6), np.uint8)  # Kernel for erosion and dilation
        mask = cv2.erode(mask, kernel, iterations=5)  # Erode to remove noise

        # Dilate to fill in the gaps
        mask = cv2.dilate(mask, kernel, iterations=9)

        # Find the contours in the mask
        contours, hierachy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
        

        emask1 = cv2.inRange(frame, low_b, high_b)
        emask1 = cv2.erode(emask1, kernel, iterations=5)
        emask1 = cv2.dilate(emask1, kernel, iterations=9)
        emask1 = emask1[0:360, 0:5]
        e1contours, hierachy = cv2.findContours(emask1, 1, cv2.CHAIN_APPROX_NONE)

        emask2 = cv2.inRange(frame, low_b, high_b)
        emask2 = cv2.erode(emask2, kernel, iterations=5)
        emask2 = cv2.dilate(emask2, kernel, iterations=9)
        emask2 = emask2[0:360, 475:480]
        e2contours, hierachy = cv2.findContours(emask2, 1, cv2.CHAIN_APPROX_NONE)


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
        #cv2.imshow("TrackMask", mask)
        cv2.imshow("Outline", frame)
        cv2.imshow("emask1", emask1)
        cv2.imshow("emask2", emask2)
        cv2.waitKey(0)
        if keyboard.is_pressed('q') :
             print("MANUAL STOP ON TRACK DETECTION")
             break
        if area >= STOP_MIN and area <= STOP_MAX:
            print("END EXECUTION ON TRACK DETECTION SUCCESS")
            break

def control():

    # Connect to remote gpio with this hostname
    pi = pigpio.pi('acecar.local')
    
    # Set the required pins to output
    pi.set_mode(INA, pigpio.OUTPUT)
    pi.set_mode(INB, pigpio.OUTPUT)
    pi.set_mode(MotorPin, pigpio.OUTPUT)
    pi.set_mode(ServoPin, pigpio.OUTPUT)

    # Drive forward
    pi.set_PWM_dutycycle(MotorPin, Power)  # Power is PWM (from 0-255)

    pi.write(INA, 0)
    pi.write(INB, 1)

    while True:

        #####################STEEERING##############################

        # Attempt to implement proportional control for steering
        MappedVal = map_range(cx, CX_MIN, CX_MAX, SERVO_MIN, SERVO_MAX)
        ClippedVal = np.clip(MappedVal, SERVO_MIN, SERVO_MAX)
        pi.set_servo_pulsewidth(ServoPin, ClippedVal)
        print("servo:", ClippedVal, " cx:", cx)


        ###########################END EXECUTION##############################
        if keyboard.is_pressed('space') :
            print("EMERGENCY STOP ON CONTROL")
            # Center the wheels and drive backards at 40 pwm for x seconds
            print("END EXECUTION ON CONTROL SUCCESS")
            pi.set_servo_pulsewidth(ServoPin, SERVO_MID)
            pi.write(INA, 1)
            pi.write(INB, 0)
            pi.set_PWM_dutycycle(MotorPin, 40)
            time.sleep(2)
            # Stop the car and clean up
            pi.set_PWM_dutycycle(MotorPin, 0)
            pi.write(INA, 0)
            pi.write(INB, 0)
            pi.stop()
            break

        if area >= STOP_MIN and area <= STOP_MAX:
            # Center the wheels and drive backards at 40 pwm for x seconds
            print("END EXECUTION ON CONTROL SUCCESS")
            pi.set_servo_pulsewidth(ServoPin, SERVO_MID)
            pi.write(INA, 1)
            pi.write(INB, 0)
            pi.set_PWM_dutycycle(MotorPin, 40)
            time.sleep(2)
            # Stop the car and clean up
            pi.set_PWM_dutycycle(MotorPin, 0)
            pi.write(INA, 0)
            pi.write(INB, 0)
            pi.stop()
            break

#############################THREADS############################################


########TRACK DETECTION#######
t_trackdetection = threading.Thread(target=track_detection)
t_trackdetection.start()

#######CONTROL/STEERING######
t_control = threading.Thread(target=control)
#t_control.start()
