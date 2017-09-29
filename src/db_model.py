from mongoengine import *

connect('flasking_db')


class User(Document):
	_id = IntField(unique = True, required = True)
	email = EmailField(required = True, unique = True)
	username = StringField(min_length = 4, max_length = 25, unique = True)
	first_name =  StringField(max_length = 50)
	last_name = StringField(max_length = 50)
	password = StringField(min_length = 8)


class Article(Document):
	_id = IntField(unique = True, required = True)
	title = StringField(max_length = 50)
	body = StringField()
	author = ReferenceField(User)
	time_published = StringField()