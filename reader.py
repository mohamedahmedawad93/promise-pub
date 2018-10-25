"""
This is the reader module
It implements the following functions 
	- `read_data`: gen. :
		Responsible for reading a headerless csv file in the format `Full Name,e-mail` and yielding each row
"""
import csv, json


def read_data(file_name):
	"""
	This is a generator function

	reads a headerless comma delimited csv file in the format
		Full name,e-mail

	input: file_name : string
	yields:
		a json {name: name(string), mail: mail(string)}
	"""
	with open(file_name, 'r') as data_file:
		data = csv.reader(data_file, delimiter=',', quotechar='"')
		for row in data:
			try:
				# just making sure that the row complies to the assumed format
				name, mail = row
				yield {'name': name, 'mail': mail}
			except ValueError as _:
				# whoops, wrong format (Python couldn't unpack the 2 values). ignore and continue
				continue
