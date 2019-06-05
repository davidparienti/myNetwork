import re

def validate_password(password):
	valid = True
	if len(password) < 8:
		valid = False
	elif re.search('[0-9]',password) is None:
		valid = False
	elif re.search('[A-Z]',password) is None:
		valid = False
	elif re.search('[a-z]',password) is None:
		valid = False    

	return valid