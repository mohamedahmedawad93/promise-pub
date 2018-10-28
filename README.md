# promise-pub

A Python system that reads events of the data.csv and publishes them over rabbitmq. This program was developed and tested using python 3.5.2


##Endpoints
|Endpoint	    | Description  						| Parameters  	|
|---------------|-----------------------------------|---------------|
|GET /			| renders the templates/index.html  | None          |
|GET /simulate/ | Creates a protocol and starts it  | timeout - int default 5 duration in seconds where the consumer should close the session after the queue is empty for x seconds after the consumer started listening on the queue|


##Usage
run
```pip install -r requirements.txt```
```python main.py```


##Modules
	- main:     Implements the endpoints handlers
	- protocol: Implements the live and batch protocol used to communicate with the consumer
	- client: 	Implements the low level communication with the consumer
	- rabbit: 	Implements the connection with rabbitmq


##Dependencies:
	- aiohttp==2.3.10
	- Jinja2==2.10
	- aiohttp-jinja2==0.15.0
	- requests==2.20.0
	- pika==0.12.0