import requests
import bs4

import time
import datetime

import threading

from pathlib import Path


def generate_config_file(home):
	print("First, you will enter which socks you want to track.")
	print("You must enter their codes separated by a comma and following the Yahoo Finance's webpage convention, as below.")
	print("'VALE3.SA,B3SA3.SA'")
	stocks = input('Stock list:')
	print("Now, enter the quantity for each stock entered, separated by a comma, as show below:")
	print("10,20")	
	quantity = input('Quantity list:')	

	stocks 		= '[stocks],' 		+ stocks 		+ ',\n'
	quantity 	= '[quantity],' 	+ quantity 		+ ',\n'

	file = open(home + '/.config/stock_email_rc', 'w')
	file.write(stocks)
	file.write(quantity)
	file.write('[hist],0.0,\n')

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
		elif line.startswith('[hist]'):
			hist = format_conf(line)

	stocks_q = dict(zip(stocks,quantity))
	
	return stocks_q, hist

balance = []

def get_stock_value(stock, quantity):
	base_url = 'https://finance.yahoo.com/quote/{}.SA?p={}.SA&.tsrc=fin-srch'
	scrape_url = base_url.format(stock,stock)
	res = requests.get(scrape_url)
	soup = bs4.BeautifulSoup(res.text, "lxml")

	stock_value = soup.select('div > span')
	actual_value = float(stock_value[10].getText())

	last_close_ext = soup.select('div span')
	last_close = last_close_ext[45].getText()

	#print((float(last_close) - float(actual_value))*int(quantity))
	balance.append((float(actual_value) - float(last_close))*int(quantity))

def write_hist(hist):
	home = str(Path.home())
	while True:
		try:
			file = open(home + '/.config/stock_email_rc', 'r')
		except:
			print("Error opening config file!")
		else:
			break

	data = file.readlines()
	file.close()

	data[-1] = '[hist],' + str(hist) + ',\n'

	while True:
		try:
			file = open(home + '/.config/stock_email_rc', 'w')
		except:
			print("Error opening config file!")
		else:
			break

	file.writelines(data)
	file.close()

def caller(stocks, hist):

	threads = []

	for stock, quantity in stocks.items():
		t = threading.Thread(target=get_stock_value, args=(stock, quantity, ))
		threads.append(t)
		t.start()

	for process in threads:
		process.join()

	historical = float(hist[0])
	final_balance = sum(balance)
	if historical > final_balance: 
		print(f'💰 ⬇ BRL {final_balance:8.2f}')
	elif historical < final_balance: 
		print(f'💰 ⬆ BRL {final_balance:8.2f}')
	else:
		print(f'💰 ➡ BRL {final_balance:8.2f}')

	write_hist(final_balance)

if __name__ == '__main__':
	d = datetime.datetime.now()
	stocks, hist = read_config()

	if (d.hour < 19 and d.hour > 9):
		caller(stocks, hist)
	else:
		print(f'💰 ➡ BRL {float(hist[0]):8.2f}')

	#caller(stocks, hist)