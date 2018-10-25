"""
This is the rabbitmq module, it uses internally one of the heavily maintained amq python client `pika`
"""
import pika, json
from settings import RABBIT


__all__ = ['RMQConnection']


class __RMQConnection:
	"""
	A rabbit mq connection class that encapsulates the settings reading, openning connection and channel
	and exposes mainly 4 methods:
		1. connect initiates a blocking rabbitmq connection and a declares a queue
		2. close   closes the rabbitmq connection
		3. send    sends a json message
		4. reset   closes the connection and re-connect
	"""
	def __init__(self):
		self._host = RABBIT.get('host', 'localhost')
		self._qname = RABBIT.get('queue', 'default_queue')
		self._connection = None
		self._channel = None
		self.connect()

	def close(self):
		if not self._connection:
			return
		self._connection.close()
		self._channel = None
		self._connection = None

	def connect(self):
		self._connection = pika.BlockingConnection(
				pika.ConnectionParameters(self._host)
			)
		self._channel = self._connection.channel()
		self._channel.queue_declare(queue=self._qname, durable=True, exclusive=False, auto_delete=False)
		self._channel.confirm_delivery()

	def send(self, msg, max_retries=5):
		if max_retries-1 < 0:
			# our reconnection base case
			return False
		if not self._channel:
			self.reset()
		if not isinstance(msg, dict):
			raise ValueError("msg should be of type `dict` not `%s`" %msg.__class__)
		try:
			return self._channel.basic_publish(exchange='',
											  routing_key=self._qname,
											  body=json.dumps(msg))
		except pika.exceptions.ConnectionClosed as e:
			self.reset()
			self.send(msg, max_retries-1)

	def reset(self):
		self.close()
		self.connect()


RMQConnection = __RMQConnection()
