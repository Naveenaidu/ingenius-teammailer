import csv
import sys
import smtplib
from jinja2 import Environment
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MY_EMAIL_ADDRESS = 'sender_email_id'
PASSWORD = 'sender_password'
HOST = 'smtp.mail.yahoo.com -  The host related to your email service'
PORT = 587

# variables to store csv details
teams = []
names = []
emails = []
ideas = []

lists=[teams,names,emails,ideas]

total_num_mails = 0

def get_contact(filename):

	with open(filename,'r') as csvfile:
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

		# Storing the row number for resume capabiltiy
		current_row = str(teams_master.index(team_name) + 1)

		#Jinja2 Template
		msg = MIMEText(
			   Environment().from_string(message_template).render(
			   	NAME=leader_name,TEAM_NAME=team_name,IDEA=idea),"html")


		# Setup the parameters of the message
		msg['From'] = MY_EMAIL_ADDRESS
		msg['To'] = email
		msg['Subject'] = "Test Mail for Ingenius"


		# Try to send the mail, else print the 
		try:
			server.send_message(msg)
			print( current_row + ". Mail Sent - " + team_name + "  -  " + email )
		except:
			print("\nMail Failure at row  " + current_row + "\n")
			print("Resume the script from row number " + current_row)
			sys.exit(0) 	

def main():

	# Change the respective HOST and PORT address
	server = server_setup(HOST,PORT)

	# Enter the CSV file name. Make sure it is present in the same directory as that of this script
	teams,names,emails,ideas = get_contact('test.csv')

	# Enter the template filename.
	# TEAM_NAME and IDEA are two variables used in the templates.
	# Use this names in your template
	message_template = read_template('template.html')

	send_mail(teams,names,emails,ideas,message_template,server)
	print("All Mails sent successfully")

main()