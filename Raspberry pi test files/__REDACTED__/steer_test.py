'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

import RPi.GPIO as GPIO
from time import sleep

in1 = 12
in2 = 19


GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
pi_pwm = GPIO.PWM(in1,1000)		#create PWM instance with frequency
pi_pwm.start(0)				#start PWM of required Duty Cycle 
while True:
    for duty in range(0,101,1):
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
        sleep(0.01)
    sleep(0.5)
    
    for duty in range(100,-1,-1):
        pi_pwm.ChangeDutyCycle(duty)
        sleep(0.01)
    sleep(0.5)
