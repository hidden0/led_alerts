#!/usr/bin/env python
from __future__ import print_function
import pickle
import os
import RPi.GPIO as GPIO
import time
import datetime
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF, 0x9400D3]
pins = {'pin_R':12, 'pin_G':21, 'pin_B':19}  # pins is a dict

GPIO.setmode(GPIO.BCM)	   # Numbers GPIOs by physical location
for i in pins:
	GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
	GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led

p_R = GPIO.PWM(pins['pin_R'], 1000)  # set Frequece to 2KHz
p_G = GPIO.PWM(pins['pin_G'], 1000)
p_B = GPIO.PWM(pins['pin_B'], 1000)
p_R.start(0)	  # Initial duty Cycle = 0(leds off)
p_G.start(0)
p_B.start(0)

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col):   # For example : col = 0x112233
	R_val = (col & 0x110000) >> 16
	G_val = (col & 0x001100) >> 8
	B_val = (col & 0x000011) >> 0

	R_val = map(R_val, 0, 255, 0, 100)
	G_val = map(G_val, 0, 255, 0, 100)
	B_val = map(B_val, 0, 255, 0, 100)

	p_R.ChangeDutyCycle(100-R_val)	 # Change duty cycle
	p_G.ChangeDutyCycle(100-G_val)
	p_B.ChangeDutyCycle(100-B_val)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
	"""Shows basic usage of the Gmail API.
	Lists the user's Gmail labels.
	"""
	os.chdir("/home/pi")
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('gmail', 'v1', credentials=creds)

	# Date setup
	aDate = datetime.datetime.now()
	bDate = aDate + datetime.timedelta(days=1)

	aDateStr = str(aDate.year)+"/"+str(aDate.month)+"/"+str(aDate.day)
	bDateStr = str(bDate.year)+"/"+str(bDate.month)+"/"+str(bDate.day)
	# Call the Gmail API
	# Get unread emails to escalations with 0 replies
	unread_escalations = service.users().messages().list(userId='me',q='after:'+aDateStr+' before:'+bDateStr+' in:escalation').execute()
	newFromNeha = service.users().messages().list(userId='me',q='from:neha.maid@meraki.net is:unread').execute()
	new_to_me = service.users().messages().list(userId='me',q='in:new-to-me is:unread').execute()
	#unread_escalations = service.users().messages().list(userId='me',q='subject:mootzig').execute()
	#results = service.users().labels().list(userId='me').execute()
	threads = unread_escalations.get('messages', [])
	personal = newFromNeha.get('messages', [])
	personal_me = new_to_me.get('messages', [])

	# LOGIC: Every email in the return results has a Thread ID. If there are any detected Thread IDs with ONE and ONLY ONE child, it is a new escalation!
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(6,GPIO.OUT)
	GPIO.output(6,GPIO.LOW)
	GPIO.setup(12,GPIO.OUT)
	GPIO.output(12,GPIO.LOW)
	GPIO.setup(23,GPIO.OUT)
	GPIO.output(23,GPIO.LOW)

	unacked = 0
	if not threads:
		print('No emails found.')
	else:
		unique_threads = []
		parent_threads = []
		escalations = {}
		x = 0
		for email in threads:
			emailData = service.users().messages().get(userId='me',id=email['id'],format='metadata').execute()
			#emailSubject = emailData['payload']['headers'][42]['value']
			#print(emailData)
			emailSubject = "None"
			for header in emailData['payload']['headers']:
				#print(header['name'] + " - " + header['value'])
				if header['name']=="Subject":
					emailSubject = header['value']
			caseNumber = re.search("[0-9]{8,9}",emailSubject)
			if not caseNumber:
				caseNumber = "0"
			else:
				caseNumber = caseNumber.group(0).lower()
			if emailSubject.lower()[0:4]!="re: ":
				escalations[x] = {'subject': emailSubject.lower(), 'case':caseNumber, 'acked':False, 'parent':True}
			else:
				escalations[x] = {'subject': emailSubject.lower(), 'case':caseNumber, 'acked':True, 'parent':False}
			#print(escalations[x])
			x+=1
		# For each parent, find a child thread
		x = 0
		y = 0
		while x < len(escalations):
			if escalations[x]['parent']==True and escalations[x]['acked']==False:
				while y < len(escalations):
					# We'll only enter this loop if the subject is the start of a thread
					# Thus, these are all reply chains. If the case number here matches a parent, it's acked
					if escalations[y]['parent']==False and escalations[y]['case']==escalations[x]['case']:
						escalations[x]['acked']=True
						#print("Found an unread parent thread with a reply...")
						break
					y+=1
			x+=1
		# Show un'ACKED escalations
		#print("--------------------------------------")
		x = 0
		while x < len(escalations):
			if(escalations[x]['acked']==False):
				unacked+=1
				print(escalations[x])
			x+=1
	# How many escalations are there?
	x = 0
	while x < unacked:
		time.sleep(1)
		GPIO.output(6,GPIO.HIGH)
		time.sleep(1)
		GPIO.output(6,GPIO.LOW)
		x+=1
	if unacked > 0:
		time.sleep(3)
		GPIO.output(6,GPIO.HIGH)
	if len(personal) > 0:
		GPIO.output(12,GPIO.HIGH)
	else:
		GPIO.output(12,GPIO.LOW)
	if len(personal_me) > 0:
		GPIO.output(23,GPIO.HIGH)
	else:
		GPIO.output(23,GPIO.LOW)

	f = 0
	try:
		for color in colors:
			setColor(color)
	except:
		p_R.stop()
		p_G.stop()
		p_B.stop()
		for i in pins:
			GPIO.output(pins[i], GPIO.HIGH)	# Turn off all leds
		GPIO.cleanup()
if __name__ == '__main__':
	main()
