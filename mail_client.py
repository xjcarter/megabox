
#!/usr/bin/python
# Adapted from http://kutuma.blogspot.com/2007/08/sending-emails-via-gmail-with-python.html

import getpass
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
import pandas
import time

gmail_user = "xjcarter@gmail.com"
gmail_pwd = "Biggie001" 

def login(user):
	global gmail_user, gmail_pwd
	gmail_user = user
	gmail_pwd = getpass.getpass('Password for %s: ' % gmail_user)

def mail(to, subject, text, attach=None):
	msg = MIMEMultipart()
	msg['From'] = gmail_user
	msg['To'] = to
	msg['Subject'] = subject
	msg.attach(MIMEText(text))
	if attach:
		part = MIMEBase('application', 'octet-stream')
		part.set_payload(open(attach, 'rb').read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
		msg.attach(part)
	mailServer = smtplib.SMTP("smtp.gmail.com", 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(gmail_user, gmail_pwd)
	mailServer.sendmail(gmail_user, to, msg.as_string())
	mailServer.close()

if __name__ == '__main__':
	mail('xjcarter@gmail.com','Test',"Hello J!")

