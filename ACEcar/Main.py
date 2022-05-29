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

#drive power (0-255)
Power = 200
pi = pigpio.pi('acecar.local')
#pi = pigpio.pi('raspberrypi.local')

pi.set_mode(INA, pigpio.OUTPUT)
pi.set_mode(INB, pigpio.OUTPUT)
pi.set_mode(drivePWM, pigpio.OUTPUT)
pi.set_mode(steerPWM, pigpio.OUTPUT)


########################MAIN##############################

def control():
    while True:
        if keyboard.is_pressed('q'):
                pi.set_PWM_dutycycle(drivePWM, 0)
                pi.write(INA, 0)
                pi.write(INB, 0)
                pi.set_servo_pulsewidth(steerPWM, 1350)
                break
        elif keyboard.is_pressed('w'):
            pi.set_PWM_dutycycle(drivePWM, Power) # int is power (from 0-255)
            pi.write(INA, 1)
            pi.write(INB, 0)

        elif keyboard.is_pressed('s'):
            pi.set_PWM_dutycycle(drivePWM, Power) # int is power (from 0-255)
            pi.write(INA, 0)
            pi.write(INB, 1)

        elif keyboard.is_pressed('a'):
            pi.set_servo_pulsewidth(steerPWM, 1150)

        elif keyboard.is_pressed('d'):
            pi.set_servo_pulsewidth(steerPWM, 1550)

        else:
            pi.set_PWM_dutycycle(drivePWM, 0)
            pi.write(INA, 0)
            pi.write(INB, 0)
            pi.set_servo_pulsewidth(steerPWM, 1350)

def main():
    global trg
    trg = 0

    cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')  # For live video
    #cap = cv2.VideoCapture('http://raspberrypi.local:8080/?action=stream')  # For live video


    low_b = np.uint8([255, 255, 255])  # color of background
    high_b = np.uint8([1, 155, 0])

    while True:

        ##read the frames and store them in the frame variable
        Ret, frame =cap.read()
        #cut off a part of the frame to not show too much
        frame = frame[150:330, 5:500]

        #find the contours of the line
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
        cv2.imshow("Mask", mask)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xff == ord('q'): #press q to quit (cv2.waitKey() needs to 1)

            cap.release()
            cv2.destroyAllWindows()
            break


def camride():
    #Drive forward
    pi.set_PWM_dutycycle(drivePWM, Power) # int is power (from 0-255)
    pi.write(INA, 1)
    pi.write(INB, 0)

    while True:
        print(trg)
        if keyboard.is_pressed('q'):
            pi.set_PWM_dutycycle(drivePWM, 0)
            pi.write(INA, 0)
            pi.write(INB, 0)
            pi.set_servo_pulsewidth(steerPWM, 1350)
            break
#update the turning sensitivity even more  - first check with track
        if trg <= 200:
            print("Turn Left")
            pi.set_servo_pulsewidth(steerPWM, 1150)

        if trg > 200 and trg < 300:
            print("On track")
            pi.set_servo_pulsewidth(steerPWM, 1350)

        if trg >= 300:
            print("Turn Right")
            pi.set_servo_pulsewidth(steerPWM, 1550)





########Detection#######
tmain = threading.Thread(target=main)
tmain.start()

#######Control/Steering######
tcamride = threading.Thread(target=camride)
tcamride.start()


##Keyboard Control/testing####
#tcontrol = threading.Thread(target=control)
#tcontrol.start()