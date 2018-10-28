"""
This is the rabbitmq module, it uses internally one of the heavily maintained amq python client `pika`
"""
import pika, json


__all__ = ['RMQConnection']


class RMQConnection:
	"""
	A rabbit mq connection class that encapsulates the settings reading, openning connection and channel
	and exposes mainly 4 methods:
		1. connect initiates a blocking rabbitmq connection and a declares a queue
		2. close   closes the rabbitmq connection
		3. send    sends a json message
		4. reset   closes the connection and re-connect
	"""
	def __init__(self, host, q):
		self._host = host
		self._qname = q
		self._connection = None
		self._channel = None

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

	def __enter__(self):
		self.connect()
		return self

	def __exit__(self, exc_type, exc_value, tb):
		if exc_type is not None:
			raise exc_type(exc_value)
		self.close()
