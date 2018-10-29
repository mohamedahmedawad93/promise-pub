"""
Client module that handles the low-level communication with the consumer server over HTTP/TCP/IP. it uses the requests library
	under the hood.

This module offers:
	1. ConsumerSession class that implements the basic communication with the consumer server
	2. create_session helper function that creates new session

use create_session to create a session if you don't know the UUID of your session otherwise use ConsumerSession directly
"""
import requests
from settings import CONSUMER_SETTINGS
from exceptions import ConsumerNotAvailableException


try:
	CONSUMER_URL = 'http://%s:%s' %(CONSUMER_SETTINGS['host'], CONSUMER_SETTINGS['port'])
except KeyError as e:
	raise ValueError("Missing host or port values in the .ini file under the consumer section")
CONSUMER_HEALTH_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('healthcheck_url', '/healthcheck/'))
CONSUMER_CREATE_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('create_url', '/create/'))
CONSUMER_DELETE_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('remove_url', '/remove/'))
CONSUMER_PROCESS_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('process_url', '/process/'))
CONSUMER_GETSESSION_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('getsession_url', '/getSession/'))
CONSUMER_OK_RESPONSE = 'OK'
CONSUMER_ERROR_RESPONSE = 'ERROR'


class ConsumerSession:
	"""
	ConsumerSession class responsible for managing the low-level communication over HTTP/TCP/IP with the golang consumer

	usage:
		The safest way to use this class is as a context manager with a `with` statement
		ex.:
			>> with session as x:
			>>     # do something with x
		If you wish to use it without a `with` statement, don't forget to invoke the `close` method afterwards.

	attributes:
		_uuid: string private attributes contains V4 UUID which looks like xxxx-xxxx-xxxx
		_timeout: integer private attribute represents durations in seconds where the consumer would disregard the session
					after x seconds of idle queues after starting processing
		_info: dictionary contains info about the session like UUID, sent messages count and received messages count

	properties:
		queue : returns the UUID of the session
		info  : returns _info but after the session has been closed

	methods:
		close(self)
			ends the session
		start_processing(self, mode='live')
			tells the consumer to start listening on the queue
	"""
	def __init__(self, _uuid, timeout):
		self._uuid = _uuid
		self._timeout = timeout
		self._info = None

	@property
	def queue(self):
	    return self._uuid

	@property
	def info(self):
		"""
		This property can only be accessed after the session has been closed, otherwise it raises a ValueError

		The reason behind this is because inserting the consumer might take a long time inserting into the database,
			so the checksum and saved values will be worthless unless the consumer has finished inserting and closed the session
		"""
		if self._info is None:
			raise ValueError("Info will only be available after closing the session")
		return self._info	    

	def close(self):
		"""
		this method closes the session with the consumer, then it set the _info dictionary attribute
		"""
		try:
			res = requests.get(CONSUMER_DELETE_URL, params={'uuid': self.queue})
		except:
			raise ConsumerNotAvailableException("Consumer not available at " + CONSUMER_URL)
		if res.text == CONSUMER_ERROR_RESPONSE:
			raise ConsumerErrorException("Consumer didn't respond with OK but returned `%s` instead \
											while closing the connection" %res.text)
		self._info = res.json()

	def start_processing(self, mode='live'):
		"""
		this method tells the consumer to start listening on the queue
		"""
		try:
			res = requests.get(CONSUMER_PROCESS_URL, params={'uuid': self.queue, 'timeout': self._timeout, 'mode': mode})
		except:
			raise ConsumerNotAvailableException("Consumer not available at " + CONSUMER_URL)
		try:
			assert res.text == CONSUMER_OK_RESPONSE
		except:
			raise ConsumerErrorException("Consumer didn't respond with OK while starting \
											to process but returned `%s` instead" %res.text)

	def __enter__(self):
		"""
		this method is invoked at the begining of a `with` statement
		We return `self` if the class is used within a context manager
		"""
		return self

	def __exit__(self, exc_type, exc_value, tb):
		"""
		this method is invoked at the end of the `with` statement
		we clean the session by calling the `close` method
		"""
		if exc_type is not None:
			raise exc_type(exc_value)
		self.close()


def create_session(timeout):
	"""
	helper function that creates a session withe consumer, gets the UUID of the session, creates a ConsumerSession instance
		and returns it

	input:
		timeout - int (seconds)
	"""
	try:
		res = requests.get(CONSUMER_CREATE_URL)
	except:
		raise ConsumerNotAvailableException("Consumer not available at " + CONSUMER_URL)
	try:
		uuid = res.json()['uuid']
	except:
		raise ConsumerErrorException("Consumer responded with wrong \
										response while creating session `%s`" %res.text)
	return ConsumerSession(uuid, timeout)
