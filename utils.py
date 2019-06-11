import re
from flask import render_template,request, redirect, url_for,flash,session , send_from_directory
def validate_password(password):
	valid = True
	if len(password) < 8:
		valid = False
	elif re.search('[[A-Za-z0-9@#$%^&+=]{8,}',password) is None:
		valid = False    

	return valid

def validate_username(username):
	valid = True
	if len(username) < 2:
		valid = False
	elif re.match("^[a-zA-Z0-9_.-]+$", username) is None:
		valid = False
	return valid

def validate_email(email):
	valid = True
	if re.match(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email) is None:
		valid = False
	return valid

def redirect_is_logged(session):

	if 'username' in session: 
		
		return redirect(url_for('index'))
	else:
		return True

def redirect_is_not_logged(session):

	if 'id' in session:
		return True
	else:
		return redirect(url_for('login'))

def allowed_file(filename,ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
