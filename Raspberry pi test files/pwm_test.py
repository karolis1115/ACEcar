from rpi_hardware_pwm import HardwarePWM
import time
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
	#steer.change_duty_cycle(100)
	#drive.change_duty_cycle(10)
	#time.sleep(1)
	#steer.change_duty_cycle(50)
	drive.change_duty_cycle(50)
	time.sleep(2)
	#steer.change_duty_cycle(10)
	#drive.change_duty_cycle(100)
	#time.sleep(1)

	steer.change_duty_cycle(0)
	drive.change_duty_cycle(0)
	time.sleep(1)

	GPIO.output(13, GPIO.HIGH)
	#GPIO.output(14, GPIO.HIGH)

	#steer.change_duty_cycle(10)
	#drive.change_duty_cycle(100)
	#time.sleep(1)
	#steer.change_duty_cycle(50)
	drive.change_duty_cycle(50)
	time.sleep(2)
	#steer.change_duty_cycle(100)
	#drive.change_duty_cycle(10)
	#time.sleep(1)
	break
steer.stop()
drive.stop()
GPIO.cleanup()
