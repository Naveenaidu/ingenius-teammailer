import os
import csv
import sys
import time
import smtplib
from jinja2 import Environment
from validate_email import validate_email
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders 

MY_EMAIL_ADDRESS = 'ingeniushack@gmail.com'
PASSWORD = 'c0mps0ch@sch@nged'
HOST = 'smtp.gmail.com'
PORT = 587

#MY_EMAIL_ADDRESS = 'naveenn_1998@yahoo.in'
#PASSWORD = 'arunkumar26'
#HOST = 'smtp.mail.yahoo.com'
#PORT = 587

# variables to store csv details
teams = []
names = []
emails = []
ideas = []
failed_emails = []
failed_row = []

lists=[teams,names,emails,ideas]

total_num_mails = 0

def get_contact(filename):

	with open(filename,'r',encoding='ISO-8859-1') as csvfile:
		csvreader = csv.reader(csvfile)

		#Extracting each data row one by one. Storing each column in specified
		# variable
		for row in csvreader:
			for i,col in enumerate(row,0):
				lists[i].append(col)

	return teams,names,emails,ideas			

def read_template(filename):
	with open(filename,'r',encoding='utf-8') as template_file:
		template_file_content = template_file.read()
	return template_file_content
	

# Setup server
def server_setup(host,port):
	server = smtplib.SMTP(host,port)
	server.starttls()
	server.login(MY_EMAIL_ADDRESS,PASSWORD)
	server.set_debuglevel(0)
	return server

# Send Mails
def send_mail(teams_master,names_master,emails_master,ideas_master,message_template,server):
	print("Enter the row number to send the mail from ")
	row_num = int(input())
	row_num = row_num - 1

	# Retaining only the required list values.
	teams = teams_master[row_num:]
	names = names_master[row_num:]
	emails = emails_master[row_num:]
	ideas = ideas_master[row_num:]


	for team_name,leader_name,email,idea in zip(teams,names,emails,ideas):
		time.sleep(10)
		# Storing the row number for resume capabiltiy
		current_row = str(teams_master.index(team_name) + 1)

		# Checking for valid format of email address
		is_valid = validate_email(email)
		if (is_valid == False):
			print( current_row + ". Mail Unsuccesfull  " + team_name + "  -  " + email )
			failed_row.append(current_row)
			failed_emails.append(email)
			continue

		# MIMEmultipart is the parent class of MIMEText. Need to be used to to attach other segments
		# of the mail.	
		msg = MIMEMultipart()

		#Jinja2 Template
		msg.attach(MIMEText(
			   Environment().from_string(message_template).render(
			   	NAME=leader_name,TEAMNAME=team_name,IDEA=idea),"html"))

		
		# Attach PDF files
		# Get the cwd
		cwd = os.getcwd()
		filename = "Invoice.pdf"
		path = cwd +"/" + filename
		attachment = open(path, "rb")

		# instance of MIMEBase and named as p 
		p = MIMEBase('application', 'octet-stream') 
  
		# To change the payload into encoded form 
		p.set_payload((attachment).read()) 

		# encode into base64 
		encoders.encode_base64(p) 
   
		p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
  
		# attach the instance 'p' to instance 'msg' 
		#msg.attach(p)  

		# Setup the parameters of the message
		msg['From'] = MY_EMAIL_ADDRESS
		msg['To'] = email
		msg['Subject'] = "inGenius 2018 selects"


		# Try to send the mail, else print the 
		try:
			server.send_message(msg)
			print( current_row + ". Mail Sent - " + team_name + "  -  " + email )
		except:
			print()
			print("\nMail Failure at row  " + current_row + "\n")
			print( current_row + ". Mail Unsuccesfull  " + team_name + "  -  " + email )
			print("Resume the script from row number " + current_row)
			continue 	

def main():

	# Change the respective HOST and PORT address
	server = server_setup(HOST,PORT)

	# Enter the CSV file name. Make sure it is present in the same directory as that of this script
	teams,names,emails,ideas = get_contact('NewParticipants.csv')

	# Enter the template filename.
	# TEAM_NAME and IDEA are two variables used in the templates.
	# Use this names in your template
	message_template = read_template('templates/wait-template.html')

	send_mail(teams,names,emails,ideas,message_template,server)

	print("The mails were succesfully sent. BRACE!! for failed emails :( ")
	print("-------------------------------------------------------------")
	print("The Unsuccesfull emails were :- ")
	for email,row_num in zip(failed_emails,failed_row):
		print(row_num +". " +email +  "\n")

main()