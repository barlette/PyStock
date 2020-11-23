valid_time = False
period_type = ''
time = '-1'

time_int = []

while period_type not in ['X', 'C', 'E']:
	period_type = input("[E]very day at a specific time, every [X] minutes, or only when you [C]all the script? [E|X|C]: ")
	period_type = period_type.upper()
if period_type == 'E':
	while valid_time == False:
		time = input('Enter the specific time [e.g. 18:30]: ')
		if ':' in time:
			time_int = time.split(':')
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
	while (time.isdigit == False) or (int(time) < 0):
		time = input('Enter the time period: ')
	time_int = 	'[time],' + time + ',\n'
else:
	time_int = 	'[time],' + time + ',\n'

period_type = '[period_type],' + period_type + ',\n'
print(period_type)
print(time_int)