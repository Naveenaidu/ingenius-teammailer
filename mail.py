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
names= [] 
sizes = []
emails = []
amounts = []
failed_emails = []
failed_row = []

lists=[teams,sizes,names,emails,amounts]

total_num_mails = 0

def get_contact(filename):

	with open(filename,'r',encoding='ISO-8859-1') as csvfile:
		csvreader = csv.reader(csvfile)

		#Extracting each data row one by one. Storing each column in specified
		# variable
		for row in csvreader:
			for i,col in enumerate(row,0):
				lists[i].append(col)

	return teams,sizes,names,emails,amounts			

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
def send_mail(teams_master,size_master,names_master,emails_master,amount_master,message_template,server):
	print("Enter the row number to send the mail from ")
	row_num = int(input())
	row_num = row_num - 1

	# Retaining only the required list values.
	teams = teams_master[row_num:]
	sizes = size_master[row_num:]
	names = names_master[row_num:]
	emails = emails_master[row_num:]
	amounts = amount_master[row_num:]



	for team_name,size,leader_name,email,amount in zip(teams,sizes,names,emails,amounts):
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
			   	NAME=leader_name,TEAMNAME=team_name,TEAMSIZE=size,AMOUNT=amount),"html"))

		
		# Attach PDF files
		# Get the cwd
		cwd = os.getcwd()
		filename = "NOC.pdf"
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
		msg.attach(p)  

		# Setup the parameters of the message
		msg['From'] = MY_EMAIL_ADDRESS
		msg['To'] = email
		msg['Subject'] = "inGenius 2018 Workshop Details and Payment Acknowledgement"


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
	teams,sizes,names,emails,amounts = get_contact('PaymentAck_1_.csv')

	# Enter the template filename.
	# TEAM_NAME and IDEA are two variables used in the templates.
	# Use this size in your template
	message_template = read_template('ack.html')

	send_mail(teams,sizes,names,emails,amounts,message_template,server)

	print("\nThe mails were succesfully sent. BRACE!! for failed emails :( ")
	print("-------------------------------------------------------------")
	print("The Unsuccesfull emails were :- ")
	for email,row_num in zip(failed_emails,failed_row):
		print(row_num +". " +email +  "\n")

main()