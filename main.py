import os
import json
import aiohttp_jinja2
import jinja2
from protocol import LiveProtocol, BatchProtocol
from aiohttp import web


MODES = ['live', 'batch']


@aiohttp_jinja2.template('result.html')
async def simulate(request):
	mode = request.GET.get('mode', 'live')
	if mode not in MODES:
		return {'status': 'Wrong mode supplied, options are `live` and `batch`', 'sent': 0, 'checksum': 0}
	protocol_class = LiveProtocol if mode=='live' else BatchProtocol
	timeout = request.GET.get('timeout', 5)
	try:
		timeout = int(timeout)
	except:
		return {'status': 'Wrong timeout value supplied, timeout must be an int', 'sent': 0, 'checksum': 0}
	proto = protocol_class('data.csv', timeout)
	res = proto.start()
	sent, checksum = 0, 0
	status = 'not-completed'
	if res:
		sent, checksum = res
		status = 'completed'
	return {'status': status, 'sent': sent, 'checksum': checksum}


@aiohttp_jinja2.template('index.html')
def index(request):
	print('serving index')
	return {'name': 'Andrew', 'surname': 'Svetlov'}


def main():
	app = web.Application()
	app.router.add_get('/', index)
	app.router.add_get('/simulate/', simulate)
	template_dir = os.path.join(os.getcwd(), 'templates')
	print('templates', template_dir)
	aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_dir))
	web.run_app(app, host='127.0.0.1', port=8000)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as _:
		RMQConnection.close()
