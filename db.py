"""
Database module used to delete employee table

It offers Employees class for external users of this module
"""
import psycopg2
from settings import DATABASE_SETTINGS
from exceptions import DatabaseNotFoundException, TableNotFoundException


class DBConnection:
	"""
	This class is the gateway between the application and the database 

	It opens a connection to the database and re-uses it over and over in a blocking manner, why are we blocking?
		- We are blocking because we don't want to handle more than one request at a time
	"""
	
	def __init__(self):
		self._host = DATABASE_SETTINGS.get('host', 'localhost')
		port = DATABASE_SETTINGS.get('port', '5432')
		try:
			# just making sure that the supplied port is an actual integer
			int(port)
		except:
			port = '5432'
		self._port = port
		self._user = DATABASE_SETTINGS['user']
		self._db = DATABASE_SETTINGS['dbname']
		print('connected to the database')
		self.connect()

	def connect(self):
		try:
			self._conn = psycopg2.connect("dbname='%s' user='%s' host='%s' port=%s password='%s'" 
										%(self._db, self._user, self._host, self._port, DATABASE_SETTINGS.get('password'))
									)
		except:
			raise DatabaseNotFoundException("Couldn't connect to the database using the credentials supplied in the .ini file")

	def execute(self, statement, *args):
		"""
		This method executes a given statement and args to guard from sql injections and returns the cursor

		IMPORTANT NOTE
			USERS OF THIS METHOD HAVE TO CLOSE THE CURSOR THEMSELVES
		"""
		try:
			cur = self._conn.cursor()
			cur.execute(statement, args)
		except psycopg2.OperationalError as e:
			self.connect()
			cur = self._conn.cursor()
			cur.execute(statement, args)			
		return cur

	def commit(self):
		self._conn.commit()


class Model:
	"""
	This is the base class for all tables in database, currently we only have employees
		It provides the database connection as a class attribute not an instance attribute, the connection
		is initialized when the model class is defined and NEVER AGAIN
	"""
	conn = DBConnection()


class Employees(Model):
	"""
	A representation of the Employees table to provide a more object oriented interface to the database
	"""

	@property
	def count(self):
		"""
		Returns the count of rows of the emploees table or raises an exception otherwise
		"""
		try:
			cur = self.conn.execute('SELECT COUNT(*) FROM EMPLOYEES')
			rows = list(cur.fetchone())
		except Exception as e:
			raise TableNotFoundException("Something went wrong while counting emploees, please check that the table exist")
		if rows:
			c = rows[0]
			cur.close()
			return c

	def clear(self):
		"""
		Deletes all records of the employee table or raises an exception otherwise
		"""
		try:
			cur = self.conn.execute('DELETE FROM EMPLOYEES')
			self.conn.commit()
			cur.close()
		except:
			raise Exception("Something went wrong while deleting emploees rows, please check that the table exist")

