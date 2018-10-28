import requests
from settings import CONSUMER_SETTINGS


try:
	CONSUMER_URL = 'http://%s:%s' %(CONSUMER_SETTINGS['host'], CONSUMER_SETTINGS['port'])
except KeyError as e:
	raise ValueError("Missing host or port values in .ini file")
CONSUMER_HEALTH_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('healthcheck_url', '/healthcheck/'))
CONSUMER_CREATE_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('create_url', '/create/'))
CONSUMER_DELETE_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('remove_url', '/remove/'))
CONSUMER_PROCESS_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('process_url', '/process/'))
CONSUMER_GETSESSION_URL = '%s%s' %(CONSUMER_URL, CONSUMER_SETTINGS.get('getsession_url', '/getSession/'))
CONSUMER_OK_RESPONSE = 'OK'
CONSUMER_ERROR_RESPONSE = 'ERROR'


class ConsumerSession:
	def __init__(self, _uuid, timeout):
		self._uuid = _uuid
		self._timeout = timeout
		self._info = None

	@property
	def queue(self):
	    return self._uuid

	def close(self):
		res = requests.get(CONSUMER_DELETE_URL, params={'uuid': self.queue})
		if res.text == CONSUMER_ERROR_RESPONSE:
			raise Exception("Couldnt close the session, received `%s`" %res.text)
		self._info = res.json()

	def start_processing(self, mode='live'):
		res = requests.get(CONSUMER_PROCESS_URL, params={'uuid': self.queue, 'timeout': self._timeout, 'mode': mode})
		assert res.text == CONSUMER_OK_RESPONSE

	@property
	def info(self):
		if self._info is None:
			raise ValueError("Info will only be available after closing the session")
		return self._info

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, tb):
		if exc_type is not None:
			raise exc_type(exc_value)
		self.close()


def create_session(timeout):
	res = requests.get(CONSUMER_CREATE_URL)
	uuid = res.json()['uuid']
	return ConsumerSession(uuid, timeout)
