# promise-pub

A Python webserver that reads events of the `data.csv` and publishes them over rabbitmq. This program was developed and tested using python 3.5.2

The reason behind using aiohttp as the webserver is to prevent multiple data transmission with the consumer at the same time since aiohttp is asynchronus and runs in a single thread. This enables us to block the whole server and serve one request at a time.

This webserver renders its HTML using `aiohttp_jinja2` library

## Database
We are using postgresql so you need to make a database with scheme identical to the scheme.sql file


## Before you start
	1. make sure you have an instance of postgresql database up and running with a database scheme identical to the one in scheme.sql file.
	2. make sure you have an instance of rabbitmq up and running
	3. make sure the consumer is up and running
	4. make sure to update the consumer, rabbit and database sections in .ini file

## .ini
#### the production.ini file needs to be set with the following sections and values
	1. rabbit:
		1. host (mandatory): the address host of the rabbitmq instance
	2. consumer:
		1. host (mandatory): the address of the consumer
		2. port (mandatory): the port of the consumer
		3. healthcheck_url (optional): default /healthcheck/
		4. create_url (optional): endpoint to create a new session default /create/
		5. remove_url (optional): endpoint to remove a session default /remove/
		6. process_url (optional): endpoint to start consuming the session queue default /process/
		7. getsession_url (optional): endpoint to get the session object default /getSession/
	3. database:
		1. host (optional): default localhost
		2. port (optional): integer default 5432
		3. dbname (mandatory): database name
		4. user (mandatory): user for the database
		5. password (mandatory): password for the database

## Endpoints
	- GET / : renders the templates/index.html
	- POST /simulate/: Simulate endpoint, creates a protocol, starts it and returns a simple html report rendered from templates/result.html, this endpoint takes as querystring:
		1. timeout int    default=5, duration in seconds where the consumer should close the session after the queue is empty for x seconds after the consumer started listening on the queue
		2. mode    string options are 'live' or 'batch', default='live'
		3. input_file a headerless csv file to process in the format name,email


## Usage
run
```
pip install -r requirements.txt
```
```
python main.py
```
Then visit http://localhost:8000

## Modules
	- main:     Implements the endpoints handlers
	- protocol: Implements the live and batch protocol used to communicate with the consumer
	- client: 	Implements the low level communication with the consumer
	- rabbit: 	Implements the connection with rabbitmq


## Dependencies:
	- aiohttp==2.3.10
	- Jinja2==2.10
	- aiohttp-jinja2==0.15.0
	- requests==2.20.0
	- pika==0.12.0
