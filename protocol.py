"""
Protocol module is responsible for orchestrating the whole data transmission thing.

This module offers two classes:
	- LiveProtocol: sends data real-time
	- BatchProtocol: sends data in batch
"""
from client import create_session
from reader import read_data
from rabbit import RMQConnection
from settings import RABBIT_SETTINGS


class ConsumerProtocol:
	"""
	ConsumerProtocol base class, this class is not supposed to be called directly by users

	attributes:
		session: ConsumerSession instance
		data:    generator function to iterate over csv lines, we use genartor function for memory management purposes
		timeout: integer duration in seconds where the consumer should close the session after the queue is empty for x seconds
		rconn:   RMQConnection instance

	Note that once the we start iterating over `data` we cannot re-iterate again, if you want to re-iterate use `data = list(proto.data)`
		But be aware that you might run out of memory

	methods:
		start(self) - this method should be implemented by subclasses otherwise it raises `NotImplementedError`
	"""
	def __init__(self, data_file, timeout):
		self.session = create_session(timeout)
		self.data = read_data(data_file)
		self.timeout = timeout
		self.rconn = RMQConnection(RABBIT_SETTINGS.get('host', 'localhost'), self.session.queue)

	def start(self):
		raise NotImplementedError("%s class which is a subclass of ConsumerProtocol should \
									implement its own start method" %self.__class__.__name__)


class LiveProtocol(ConsumerProtocol):
	"""
	A subclass of ConsumerProtocol, implements processing the csv in live mode.

	Live mode: We tell the consumer to start listening before we even begin to send data over the queue
		this forces the consumer to read the data one by one in real time

	methods:
		overrides start(self)
	"""
	
	def start(self):
		"""
		Procedure
			1. opens rabbitmq connection
			2. creates a new session with the consumer
			3. tells the consumer to start listening on the queue
			4. send the data one by one
			5. returns total number of rows sent + session info		
		"""
		i = None
		with self.rconn as rconn:
			with self.session as session:
				session.start_processing()
				i = 0
				for row in self.data:
					i += self.rconn.send(row)
		return i, self.session.info


class BatchProtocol(ConsumerProtocol):
	"""
	A subclass of ConsumerProtocol, implements processing the csv in batch mode.

	Batch mode: We send the data over the queue first then we tell the consumer to start listening on the queue
		this forces the consumer to read the data in batch

	methods:
		overrides start(self)
	"""	
	
	def start(self):
		"""
		Procedure
			1. opens rabbitmq connection
			2. creates a new session with the consumer
			3. send the data to the queue
			4. tells the consumer to start listening on the queue
			5. returns total number of rows sent + session info		
		"""
		i = None
		with self.rconn as rconn:
			with self.session as session:
				i = 0
				for row in self.data:
					i += self.rconn.send(row)
				session.start_processing(mode='batch')
		return i, self.session.info
