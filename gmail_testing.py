#!/usr/bin/env python
from __future__ import print_function
import pickle
import os.path
import datetime
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
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
	aDate = datetime.datetime.now()
	bDate = aDate + datetime.timedelta(days=1)
	
	# Call the Gmail API
	aDateStr = str(aDate.year)+"/"+str(aDate.month)+"/"+str(aDate.day)
	bDateStr = str(bDate.year)+"/"+str(bDate.month)+"/"+str(bDate.day)
	# Call the Gmail API
	# Get unread emails to escalations with 0 replies
	results = service.users().messages().list(userId='me',q='after:'+aDateStr+' before:'+bDateStr+' in:escalation').execute()
	emails = results.get('messages', [])

	if not emails:
		print('No emails found.')
	else:
		print('Emails:')
		for mail in emails:
			print(mail)

if __name__ == '__main__':
	main()
