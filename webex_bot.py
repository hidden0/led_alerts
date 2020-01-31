#!/usr/bin/env python
#defining the RPi's pins as Input / Output
import RPi.GPIO as GPIO

#importing the library for delaying command.
import time
import requests
import re
import json
import sys

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
r = requests.get('https://api.ciscospark.com/v1/messages?max=1&roomId=Y2lzY29zcGFyazovL3VzL1JPT00vYjk4MWU5NzAtNDQ3Ni0xMWVhLWI2YjctMTEzZjlmN2YyOTQy&mentionedPeople=me', headers={'Authorization': 'Bearer '+str(daveToken).rstrip()})
json_data = json.loads(r.text)

for item in json_data['items']:
	message = item['text']
	print(message)
	regex = r"\b(?:red|blue|green|yellow|orange|purple|white)\b"

	matches = re.finditer(regex, message, re.MULTILINE)

	for matchNum, match in enumerate(matches, start=1):
		#print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
		print (match.group(0))
		"""for groupNum in range(0, len(match.groups())):
			groupNum = groupNum + 1

			print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))"""
exit()
try:
	#we are starting with the loop
	RED.start(1)
	GREEN.start(1)
	BLUE.start(1)
	while RUNNING:
		#lighting up the pins. 100 means giving 100% to the pin

		#For anode RGB LED users, if you want to start with RED too the only thing to be done is defining RED as one and GREEN and BLUE as 100.
		for x in range(1,100):
			RED.ChangeDutyCycle(x)
			GREEN.ChangeDutyCycle(101-x)
			BLUE.ChangeDutyCycle(1)
			time.sleep(0.05)
		time.sleep(0.005)

except KeyboardInterrupt:
	# the purpose of this part is, when you interrupt the code, it will stop the while loop and turn off the pins, which means your LED won't light anymore
	RUNNING = False
	GPIO.cleanup()
