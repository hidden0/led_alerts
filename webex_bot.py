#!/usr/bin/env python
#defining the RPi's pins as Input / Output
import RPi.GPIO as GPIO

#importing the library for delaying command.
import time
import requests
import re
import json
import sys

# colors
colors = { 'red':0xFF0000, 'green':0x00FF00, 'blue':0x0000FF, 'yellow':0xFFFF00, 'teal':0x00FFFF, 'purple':0xFF00FF, 'white':0xFFFFFF, 'navy':0x9400D3 }

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
Freq = 1000

#defining the pins that are going to be used with PWM
RED = GPIO.PWM(red, Freq)
GREEN = GPIO.PWM(green, Freq)
BLUE = GPIO.PWM(blue, Freq)

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col):   # For example : col = 0x112233
	R_val = (col & 0x110000) >> 16
	G_val = (col & 0x001100) >> 8
	B_val = (col & 0x000011) >> 0

	R_val = map(R_val, 0, 255, 0, 100)
	G_val = map(G_val, 0, 255, 0, 100)
	B_val = map(B_val, 0, 255, 0, 100)

	RED.ChangeDutyCycle(100-R_val)     # Change duty cycle
	GREEN.ChangeDutyCycle(100-G_val)
	BLUE.ChangeDutyCycle(100-B_val)



rVal = 1
gVal = 100
bVal = 100
x = 1
rValMod = 1

# Setup Webex bot listeners
# First arg should be token, second id
daveToken = ""
daveId = ""
roomId = ""
apiUrl = "https://api.ciscospark.com/v1/"
apiAction = "messages"
params = "?roomId=Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0&mentionedPeople=Y2lzY29zcGFyazovL3VzL1BFT1BMRS8yNDlmNzRkOS1kYjhhLTQzY2EtODk2Yi04NzllZDI0MGFjNTM&before=2016-04-21T19:01:55.966Z&beforeMessage=Y2lzY29zcGFyazovL3VzL01FU1NBR0UvOTJkYjNiZTAtNDNiZC0xMWU2LThhZTktZGQ1YjNkZmM1NjVk&max=100"


f = open(sys.argv[1], "r")
daveToken = (f.read())
f.close()
f = open(sys.argv[2], "r")
daveId = (f.read())
f.close()
f = open(sys.argv[3], "r")
roomId = (f.read())
f.close()

fullQuery = apiUrl + apiAction + params
m = {'roomId': roomId.rstrip(), 'mentionedPeople': daveId.rstrip()}

try:
	#we are starting with the loop
	RED.start(1)
	GREEN.start(1)
	BLUE.start(1)
	while RUNNING:
		#lighting up the pins. 100 means giving 100% to the pin
		r = requests.get('https://api.ciscospark.com/v1/messages?max=1&roomId=Y2lzY29zcGFyazovL3VzL1JPT00vYjk4MWU5NzAtNDQ3Ni0xMWVhLWI2YjctMTEzZjlmN2YyOTQy&mentionedPeople=me', headers={'Authorization': 'Bearer '+str(daveToken).rstrip()})
		json_data = json.loads(r.text)
		selectedColor = colors['green']

		for item in json_data['items']:
			message = item['text']
			print(message)
			regex = r"\b(?:red|blue|green|yellow|orange|purple|white)\b"

			matches = re.finditer(regex, message, re.MULTILINE)

			for matchNum, match in enumerate(matches, start=1):
				#print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
				setColor(colors[(match.group(0))])

		time.sleep(2)

except KeyboardInterrupt:
	# the purpose of this part is, when you interrupt the code, it will stop the while loop and turn off the pins, which means your LED won't light anymore
	RUNNING = False
	GPIO.cleanup()
