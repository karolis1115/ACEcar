#import cv2
import time
import pigpio
import keyboard

steerPWM =12
steerDirrection= 5
drivePWM =13
driveDirrection= 6


pi = pigpio.pi('raspberrypi.local')
pi.set_mode(steerDirrection, pigpio.OUTPUT)
pi.set_mode(steerPWM, pigpio.OUTPUT)
pi.set_mode(driveDirrection, pigpio.OUTPUT)
pi.set_mode(drivePWM, pigpio.OUTPUT)

while True:
    if keyboard.is_pressed('w'):
        pi.write(driveDirrection,1)
        pi.write(drivePWM,0)
   
    elif keyboard.is_pressed('s'):
        pi.write(driveDirrection,0)
        pi.write(drivePWM,1)


    elif keyboard.is_pressed('a'):
        pi.write(steerDirrection,0)
        pi.set_PWM_dutycycle(steerPWM, 255)

   
    elif keyboard.is_pressed('d'):
        pi.set_PWM_dutycycle(steerDirrection, 255)
        pi.write(steerPWM,0)

    else:
        pi.write(steerDirrection,0)
        pi.write(steerPWM,0)
        pi.write(driveDirrection,0)
        pi.write(drivePWM,0)