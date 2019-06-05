from flask import render_template,request, redirect, url_for,flash,session , send_from_directory
from database import app, db, User, Post, Like, Comment, Friend
from utils import validate_password

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def index():
  page_name = "Home"
  return render_template('index.html',session=session,page_name=page_name)

@app.route('/login',methods = ['GET', 'POST'])
def login_sign_up():
	page_name = "login - sign up"

	if request.form['form'] == 'sign_up'
		fullname = request.form['fullname'],
		username = request.form['username'],
		email = request.form['email']
		password = request.form['password']
		repeat_password = request.form['repeat_password']

		if User.query.filter_by(username=request.form['username']).first() == None:
			if validate_password(password):
				user = User(username=request.form['username'],password=password)
				# flash('User saved succefuly')
				db.session.add(user)
				db.session.commit()
				session['username'] = username
				return redirect(url_for('index'))
			else:
				flash(' password is too weak')
		else:
			flash('Username already exist')
	return render_template('signup.html')


	else:
		user = User.query.filter_by(
				username=request.form['username'],
				password=request.form['password']
			).first()
 
  return render_template('login.html',session=session,page_name=page_name)


@app.route('/logout')
def logout():
	page_name = "Log Out"
	session.pop('username')
	return redirect(url_for('index'))

