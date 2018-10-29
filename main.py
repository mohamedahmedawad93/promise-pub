"""
Entry point of this program

It starts an aiohttp server listening on port `8000` with 2 endpoints
	GET /          - Index endpoint, it renders the html file in templates/index.html
	POST /simulate/ - Simulate endpoint, creates a protocol, starts it and returns a simple html report rendered from
					templates/result.html
				    - this endpoint takes as querystring
				   	  1. timeout int    default=5
								   	  duration in seconds where the consumer should close the session after the queue is empty 
								   		  for x seconds after the consumer started listening on the queue
				   	  2. mode    string options are 'live' or 'batch', default='live'
				   	  3. input_file a headerless csv file to process in the format name,email

The reason behind using aiohttp is to prevent multiple data transmission with the consumer at the same time since aiohttp 
	is asynchronus and runs in a single thread. This enables us to block the whole server and serve one request at a time.


This webserver renders its HTML using aiohttp_jinja2 library

usage:
	$ python main.py
"""
import os
import time
import json
import aiohttp_jinja2
import jinja2
from protocol import LiveProtocol, BatchProtocol
from aiohttp import web
from db import Employees
from exceptions import ConsumerNotAvailableException, ConsumerErrorException, RabbitmqNotAvailableException


MODES = ['live', 'batch']
UPLOADS_PATH = os.path.join(os.getcwd(), 'uploads')


def save_csv(content):
	name = os.path.join(UPLOADS_PATH, '%d.csv' %time.time())
	with open(name, 'wb') as f:
		f.write(content)
	return name


@aiohttp_jinja2.template('result.html')
async def simulate(request):
	data = await request.post()
	mode = data.get('mode', 'live')
	clear = data.get('clear', '') == 'true'
	try:
		input_file = data['input_file'].file
	except:
		return {'status': 'Please supply a csv file to process'}
	try:
		content = input_file.read()
		file_path = save_csv(content)
	except:
		return {'status': "Couldn't parse the csv file supplied"}
	employees = Employees()
	if clear:
		employees.clear()
	if mode not in MODES:
		return {'status': 'Wrong mode supplied, options are `live` and `batch`', 'sent': 0, 'checksum': 0}
	protocol_class = LiveProtocol if mode=='live' else BatchProtocol
	timeout = data.get('timeout', 5)
	try:
		timeout = int(timeout)
	except:
		return {'status': 'Wrong timeout value supplied, timeout must be an int', 'sent': 0, 'checksum': 0}
	try:
		proto = protocol_class(file_path, timeout)
	except ConsumerNotAvailableException as e0:
		return {'status': str(e0), 'sent': 0, 'checksum': 0}
	try:
		res = proto.start()
	except ConsumerNotAvailableException as e1:
		return {'status': str(e1), 'sent': 0, 'checksum': 0}
	except ConsumerErrorException as e2:
		return {'status': str(e2), 'sent': 0, 'checksum': 0}
	except RabbitmqNotAvailableException as e3:
		return {'status': str(e3), 'sent': 0, 'checksum': 0}
	except Exception as e4:
		return {'status': "Unknown error occured", 'sent': 0, 'checksum': 0}
	sent, info = 0, {}
	status = 'not-completed'
	if res:
		sent, info = res
		status = 'completed'
	info['db_count'] = employees.count
	return {'status': status, 'sent': sent, 'info': info}


@aiohttp_jinja2.template('index.html')
def index(request):
	return {}


def main():
	app = web.Application()
	app.router.add_get('/', index)
	app.router.add_post('/simulate/', simulate)
	template_dir = os.path.join(os.getcwd(), 'templates')
	aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_dir))
	web.run_app(app, host='127.0.0.1', port=8000)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as _:
		RMQConnection.close()
