from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///socialNetwork.db'
db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	full_name = db.Column(db.String(80),  nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(20),  nullable=False)
	created = db.Column(db.DateTime(), default=datetime.datetime.now())
	profil_media = db.Column(db.String(80), unique=True, nullable=True)


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	title = db.Column(db.Text)
	message = db.Column(db.Text)
	created = db.Column(db.DateTime, default=datetime.datetime.now())

class Jaime(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	created = db.Column(db.DateTime, default=datetime.datetime.now())

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	message = db.Column(db.Text)
	created = db.Column(db.DateTime, default=datetime.datetime.now())
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


class Followerfollowing(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	user_id_2 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	created = db.Column(db.DateTime, default=datetime.datetime.now())

