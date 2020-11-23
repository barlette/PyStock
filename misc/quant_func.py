import requests
import bs4
import smtplib
import getpass

import time
import schedule
import datetime

from email.message import EmailMessage
from email.parser import BytesParser, Parser
from email.policy import default
from email.mime.text import MIMEText
from pathlib import Path


def generate_config_file(home):
	print("First, you will enter which socks you want to track.")
	print("You must enter their codes separated by a comma and following the Yahoo Finance's webpage convention, as below.")
	print("'VALE3.SA,B3SA3.SA'")
	stocks = input('Stock list:')
	print("Now, enter the quantity for each stock entered, separated by a comma, as show below:")
	print("10,20")	
	quantity = input('Quantity list:')	
	sender = input("Now enter your email address:")
	password = getpass.getpass("Enter your password: ")
	recipients = input("Enter a list of email addresses you want to send the stock report:")
	print("When would you like for the email to be sent?")

	valid_time = False
	period_type = ''
	time_p = '-1'

	time_int = []

	while period_type not in ['X', 'C', 'E']:
		period_type = input("[E]very day at a specific time, every [X] minutes, or only when you [C]all the script? [E|X|C]")

	if period_type == 'E':
		while valid_time == False:
			time_p = input('Enter the specific time [e.g. 18:30]: ')
			if ':' in time_p:
				time_int = time_p.split(':')
				if time_int[0].isdigit() and time_int[1].isdigit():
					if int(time_int[0]) > 24:
						time_int[0] == '24'
					elif int(time_int[0]) < 0:
						time_int[0] == '0'
					if int(time_int[1]) > 60:
						time_int[1] == '60'
					elif int(time_int[1]) < 0:
						time_int[1] == '0'
					valid_time = True
		time_int 	= '[time],' + time_int[0] + ':' + time_int[1] + ',\n'
	elif period_type == 'X':
		while (time_p.isdigit == False) or (int(time_p) < 0):
			time_p = input('Enter the time period: ')
		time_int = 	'[time],' + time_p + ',\n'
	else:
		time_int = 	'[time],' + time_p + ',\n'



	stocks 		= '[stocks],' 		+ stocks 		+ ',\n'
	quantity 	= '[quantity],' 	+ quantity 		+ ',\n'
	sender 		= '[sender],' 		+ sender 		+ ',\n'
	password 	= '[password],' 	+ password 		+ ',\n'
	recipients 	= '[recipients],' 	+ recipients 	+ ',\n'
	period_type = '[period_type],' 	+ period_type 	+ ',\n'
	

	file = open(home + '/.config/stock_email_rc', 'w')
	file.write(stocks)
	file.write(quantity)
	file.write(sender)
	file.write(password)
	file.write(recipients)
	file.write(period_type)
	file.write(time_int)

	file.close()

	print("REMEMBER: You can always edit your config file by accessing the 'stock_email_rc' file in your .config folder inside your $HOME.")

def format_conf(line):

	output = line.split(',')
	output.pop(0)
	output.pop(len(output)-1)
	return output

def read_config():

	home = str(Path.home())
	while True:
		try:
			file = open(home + '/.config/stock_email_rc', 'r')
		except:
			print("Config file does not exist!\nLet's create a new one.")
			generate_config_file(home)
		else:
			#print('Config file read successfully.')
			break	

	for line in file:
		if line.startswith('[stocks]'):
			stocks = format_conf(line)
		elif line.startswith('[quantity]'):
			quantity = format_conf(line)
		elif line.startswith('[sender]'):
			sender = format_conf(line)
		elif line.startswith('[password]'):
			password = format_conf(line)
		elif line.startswith('[recipients]'):
			recipients = format_conf(line)
		elif line.startswith('[period_type]'):
			period_type = format_conf(line)
		elif line.startswith('[time]'):
			time_p = format_conf(line)

	stocks_q = dict(zip(stocks,quantity))
	

	return stocks_q, sender, password, recipients, period_type, time_p

def get_stock_values(stocks):

	base_url = 'https://finance.yahoo.com/quote/{}?p={}&.tsrc=fin-srch'

	percentage_total = 0.0

	subject = []

	#print(stocks)
	all_last_closed = []
	all_actual_value = []

	for stock, quantity in stocks.items():
		scrape_url = base_url.format(stock,stock)
		res = requests.get(scrape_url)
		soup = bs4.BeautifulSoup(res.text, "lxml")
		stock_value = soup.select('div > span')

		last_close_ext = soup.select('div span')
		last_close = last_close_ext[44].getText()

		actual_value = float(stock_value[9].getText())
		fluct = stock_value[10].getText()
		percentage = fluct.split(" ")

		percentage_form = percentage[1].replace('(','').replace(')','').replace('%', '')

		if percentage_form.startswith('+'):
			percentage_form = percentage_form.replace('+', '')

		percentage_number = float(percentage_form)

		total_last_closed = float(quantity) * float(last_close)
		total_actual_value = float(quantity) * float(actual_value)

		all_last_closed.append(total_last_closed)
		all_actual_value.append(total_actual_value)

		subject.append(f'{stock} : BRL {actual_value:.2f} {percentage_number: 4.2f}% {float(last_close):.2f} {int(quantity):3d} {total_last_closed:7.2f} {total_actual_value:7.2f}\n')

		percentage = fluct.split(" ")

		percentage_form = percentage[1].replace('(','').replace(')','').replace('%', '')

		if percentage_form.startswith('+'):
			percentage_form = percentage_form.replace('+', '')

		percentage_number = float(percentage_form)

	sum_all_actual_value = sum(all_actual_value)
	sum_all_last_closed = sum(all_last_closed)

	subject.append(f'Balance: {sum_all_actual_value:8.2f} + {sum_all_last_closed:8.2f} = {(sum_all_actual_value - sum_all_last_closed):8.2f} ')

	total_sub = ''.join(subject)
	return total_sub

def send_email(total_sub, sender, recipients, password):
	subject = "Ações " + datetime.datetime.today().strftime("%d/%m/%Y")
	body = total_sub

	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = sender[0]
	msg['To'] = ", ".join(recipients)

	session = smtplib.SMTP('smtp.gmail.com', 587)
	session.starttls()
	session.login(sender[0], password[0])
	send_it = session.sendmail(sender[0], recipients, msg.as_string())
	session.quit()

def caller(stocks, sender, recipients, password):
	total_sub = get_stock_values(stocks)
	send_email(total_sub, sender, recipients, password)	

if __name__ == '__main__':
	stocks, sender, password, recipients, period_type, time_p = read_config()
	
	if period_type[0] == 'C':
		caller(stocks, sender, recipients, password)
	elif period_type[0] == 'E':
		schedule.every().day.at(time_p[0]).do(caller,stocks, sender, recipients, password)
	elif period_type[0] == 'X':
		schedule.every(int(time_p[0])).minutes.do(caller, stocks, sender, recipients, password)

	if period_type[0] in ['E', 'X']:
		while True:
			schedule.run_pending()
			time.sleep(60)
