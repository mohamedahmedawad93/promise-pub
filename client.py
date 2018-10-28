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


class ConsumerSession:
	def __init__(self, _uuid, timeout):
		self._uuid = _uuid
		self._timeout = timeout

	@property
	def queue(self):
	    return self._uuid

	def delete(self):
		res = requests.get(CONSUMER_DELETE_URL, params={'uuid': self.queue})
		assert res.text == CONSUMER_OK_RESPONSE

	def start_processing(self, mode='live'):
		res = requests.get(CONSUMER_PROCESS_URL, params={'uuid': self.queue, 'timeout': self._timeout, 'mode': mode})
		assert res.text == CONSUMER_OK_RESPONSE

	@property
	def check_sum(self):
		res = requests.get(CONSUMER_GETSESSION_URL, params={'uuid': self.queue})
		print(res.text)
		try:
			json = res.json()
			print('session entity', json)
			return json.get('checksum', 0)
		except:
			return 0

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, tb):
		if exc_type is not None:
			raise exc_type(exc_value)
		self.delete()


def create_session(timeout):
	res = requests.get(CONSUMER_CREATE_URL)
	uuid = res.json()['uuid']
	return ConsumerSession(uuid, timeout)
