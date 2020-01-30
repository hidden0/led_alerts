#!/usr/bin/env python
from __future__ import print_function
import pickle
import os
import RPi.GPIO as GPIO
import time
import datetime
import re
import threading
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF, 0x9400D3]
pins = {'pin_R':12, 'pin_G':19, 'pin_B':21}  # pins is a dict

GPIO.setmode(GPIO.BCM)	   # Numbers GPIOs by physical location
for i in pins:
	GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
	GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led

p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
p_G = GPIO.PWM(pins['pin_G'], 2000)
p_B = GPIO.PWM(pins['pin_B'], 2000)
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
	while True:
		"""Shows basic usage of the Gmail API.
		Lists the user's Gmail labels.
		"""
		creds = None
		emails = None
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

		aDateStr = str(int(time.time())-(60*60*4))

		# Call the Gmail API
		# Get unread emails to escalations with 0 replies
		results = service.users().messages().list(userId='me',q='after:'+aDateStr+' in:escalation').execute()
		emails = results.get('messages', [])

		threads = {}

		if not emails:
			print('No emails found.')
		else:
			#print('Emails:')
			y = 0
			for mail in emails:
				threads[y] = { 'emailId':mail['id'], 'threadId':mail['threadId'], 'acked': False, 'subject': 'none', 'case': '0', 'parent':False }
				# Find a unique thread id
				x = 0
				match = 0
				found = False
				while x < len(emails):
					#print("Checking " + str(mail['threadId']) + " against " + str(emails[x]['threadId']))
					if str(mail['threadId']) == str(emails[x]['threadId']):
						#print("==MATCH==")
						match+=1
					if match >= 2:
						#print (str(mail['threadId']) + " is ACKed")
						threads[y]['acked']=True
						match = 0
						break
					x+=1
				y+=1

			# We have a trimmed list to look at now
			y=0
			while y < len(threads):
				caseNumber = "0"
				emailSubject = "None"
				if threads[y]['acked']==False:
					# Do some more checking
					emailData = service.users().messages().get(userId='me',id=threads[y]['emailId'],format='metadata').execute()
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
						threads[y] = {'subject': emailSubject.lower(), 'case':caseNumber, 'acked':False, 'parent':True}
						#print(escalations[x])
					else:
						threads[y] = {'subject': emailSubject.lower(), 'case':caseNumber, 'acked':True, 'parent':False}
					#print(escalations[x])
				y+=1

			# Dump array
			y=0
			unacked = 0
			while y < len(threads):
				#print(threads[y])
				if threads[y]['acked']==False:
					unacked+=1
				y+=1

			# Check unacked escalations
			if unacked > 0:
				setColor(colors[0])
				print(str(int(time.time())) + " Red")
			else:
				setColor(colors[6])
				print(str(int(time.time())) + " White")
			time.sleep(10.0)

if __name__ == '__main__':
	main()
