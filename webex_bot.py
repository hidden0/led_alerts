#!/usr/bin/env python
#defining the RPi's pins as Input / Output
import RPi.GPIO as GPIO

#importing the library for delaying command.
import time

#used for GPIO numbering
GPIO.setmode(GPIO.BCM)

#closing the warnings when you are compiling the code
GPIO.setwarnings(False)

RUNNING = True

#defining the pins
green = 6
red = 5
blue = 13

#defining the pins as output
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)

#choosing a frequency for pwm
Freq = 100

#defining the pins that are going to be used with PWM
RED = GPIO.PWM(red, Freq)
GREEN = GPIO.PWM(green, Freq)
BLUE = GPIO.PWM(blue, Freq)

rVal = 1
gVal = 100
bVal = 100
x = 1
rValMod = 1

try:
	#we are starting with the loop
	RED.start(1)
	GREEN.start(1)
	BLUE.start(1)
	while RUNNING:
		#lighting up the pins. 100 means giving 100% to the pin

		#For anode RGB LED users, if you want to start with RED too the only thing to be done is defining RED as one and GREEN and BLUE as 100.
		rVal = rVal - (1 * rValMod)
		if rVal < 0:
			rValMod = -1
			rVal = 0
		if rVal > 100:
			rValMod = 1
			rVal = 100
		RED.ChangeDutyCycle(rVal)
		GREEN.ChangeDutyCycle(gVal)
		BLUE.ChangeDutyCycle(bVal)
		time.sleep(0.005)

except KeyboardInterrupt:
	# the purpose of this part is, when you interrupt the code, it will stop the while loop and turn off the pins, which means your LED won't light anymore
	RUNNING = False
	GPIO.cleanup()
