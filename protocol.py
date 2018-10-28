from client import create_session
from reader import read_data
from rabbit import RMQConnection
from settings import RABBIT_SETTINGS


class ConsumerProtocol:
	def __init__(self, data_file, timeout):
		self.session = create_session(timeout)
		self.data = read_data(data_file)
		self.timeout = timeout
		self.rconn = RMQConnection(RABBIT_SETTINGS.get('host', 'localhost'), self.session.queue)

	def start(self):
		raise NotImplementedError("%s class which is a subclass of ConsumerProtocol should \
									implement its own start method" %self.__class__.__name__)


class LiveProtocol(ConsumerProtocol):
	
	def start(self):
		i, check_sum = None, None
		with self.rconn as rconn:
			with self.session as session:
				session.start_processing()
				i = 0
				for row in self.data:
					print('sending row', row)
					i += self.rconn.send(row)
				check_sum = session.check_sum
		return i, check_sum


class BatchProtocol(ConsumerProtocol):
	
	def start(self):
		i, check_sum = None, None
		with self.rconn as rconn:
			with self.session as session:
				i = 0
				for row in self.data:
					print('sending row', row)
					i += self.rconn.send(row)
				session.start_processing(mode='batch')
				check_sum = session.check_sum
		return i, check_sum
