from protocol import LiveProtocol, BatchProtocol


def test_protocol(protocol_class, data_file):
	proto = protocol_class('data.csv')
	res = proto.start()
	if res:
		sent, checksum = res
		print('sent:', sent, 'received', checksum)


def main():
	test_protocol(LiveProtocol, 'data.csv')
	test_protocol(BatchProtocol, 'data.csv')


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as _:
		RMQConnection.close()
