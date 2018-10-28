import configparser


def validate_ini(c):
	if 'rabbit' not in c:
		raise Exception("the .ini file must contain a rabbit section")
	if 'consumer' not in config:
		raise Exception("the .ini file must contain a consumer section")


config = configparser.ConfigParser()
config.read('production.ini')
validate_ini(config)


################################################ RABBITMQ SETTINGS ################################################
RABBIT_SETTINGS = dict(config['rabbit'])


################################################ CONSUMER SETTINGS ################################################
CONSUMER_SETTINGS = dict(config['consumer'])
