from rpi_hardware_pwm import HardwarePWM
import time
import keyboard
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.OUT) #driving dirrection
GPIO.setup(14, GPIO.OUT) #steering dirrection

steer = HardwarePWM(pwm_channel=0, hz=60) #steering motor
drive = HardwarePWM(pwm_channel=1, hz=60) #drive motor

GPIO.output(13, GPIO.LOW)
GPIO.output(14, GPIO.LOW)

steer.start(0)
drive.start(0)

while True:
	if keyboard.is_pressed('x'):
		print("If condition is met")
steer.stop()
drive.stop()
GPIO.cleanup()
