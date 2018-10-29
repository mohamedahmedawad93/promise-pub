class DatabaseNotFoundException(Exception):
	pass


class TableNotFoundException(Exception):
	pass


class ConsumerNotAvailableException(Exception):
	pass


class ConsumerErrorException(Exception):
	pass


class RabbitmqNotAvailableException(Exception):
	pass