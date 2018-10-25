from reader import read_data
from rabbit import RMQConnection


def main():
	rows, sent = 0, 0
	for row in read_data('data.csv'):
		rows += 1
		status = RMQConnection.send(row)
		sent += status
		if not status:
			print('couldnt send', status)		
	print('total rows', rows, 'sent', sent)
	RMQConnection.close()


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as _:
		RMQConnection.close()
