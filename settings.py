"""
Parses the production.ini file and loads the sections into RABBIT_SETTINGS and CONSUMER_SETTINGS dictionaries
"""
import configparser


def validate_ini(c):
	if 'rabbit' not in c:
		raise Exception("the .ini file must contain a rabbit section")
	if 'consumer' not in config:
		raise Exception("the .ini file must contain a consumer section")
	if 'database' not in config:
		raise Exception("the .ini file must contain a database section")


config = configparser.ConfigParser()
config.read('production.ini')
validate_ini(config)


################################################ RABBITMQ SETTINGS ################################################
RABBIT_SETTINGS = dict(config['rabbit'])


################################################ CONSUMER SETTINGS ################################################
CONSUMER_SETTINGS = dict(config['consumer'])


################################################ DATABASE SETTINGS ################################################
DATABASE_SETTINGS = dict(config['database'])
