import requests
import bs4
import smtplib
import getpass
from datetime import date

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
	sender = input("Now enter your email address:")
	password = getpass.getpass("Enter your password: ")
	recipients = input("Lastly, enter a list of email addresses you want to send the stock report:")
	
	stocks 		= '[stocks],' + stocks + ',\n'
	sender 		= '[sender],' + sender + ',\n'
	password 	= '[password],' + password + ',\n'
	recipients 	= '[recipients],' + recipients + ',\n'

	file = open(home + '/.config/stock_email_rc', 'w')
	file.write(stocks)
	file.write(sender)
	file.write(password)
	file.write(recipients)

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
			print('Config file read successfully.')
			break	

	for line in file:
		if line.startswith('[stocks]'):
			stocks = format_conf(line)
		elif line.startswith('[sender]'):
			sender = format_conf(line)
		elif line.startswith('[password]'):
			password = format_conf(line)
		elif line.startswith('[recipients]'):
			recipients = format_conf(line)

	return stocks, sender, password, recipients

def get_stock_values(stocks):

	base_url = 'https://finance.yahoo.com/quote/{}?p={}&.tsrc=fin-srch'

	percentage_total = 0.0

	subject = []

	for stock in stocks:
		scrape_url = base_url.format(stock,stock)
		res = requests.get(scrape_url)

		soup = bs4.BeautifulSoup(res.text, "lxml")

		stock_value = soup.select('div > span')
		subject.append(stock + ' : ' + stock_value[9].getText() + " " + stock_value[10].getText() + "\n")


		percentage = stock_value[10].getText().split(" ")

		percentage_form = percentage[1].replace('(','').replace(')','').replace('%', '')

		if percentage_form.startswith('+'):
			percentage_form = percentage_form.replace('+', '')

		percentage_number = float(percentage_form)
		percentage_total += percentage_number

	subject.append('Balance : ' + str("%.2f" % percentage_total) + '%')

	total_sub = ''.join(subject)
	return total_sub

def send_email(total_sub, sender, recipients, password):
	subject = "Ações " + date.today().strftime("%d/%m/%Y")
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

if __name__ == '__main__':
	stocks, sender, password, recipients = read_config()
	total_sub = get_stock_values(stocks)
	send_email(total_sub, sender, recipients, password)
