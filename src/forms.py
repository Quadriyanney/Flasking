from wtforms import Form, StringField, TextAreaField, PasswordField, validators


class RegisterForm(Form):
	first_name = StringField('First Name', [validators.length(min = 1, max = 50)])
	last_name = StringField('Last Name', [validators.length(min = 1, max = 50)])
	email = StringField('Email', [validators.length(min = 6, max = 50)])
	username = StringField('Username', [validators.length(min = 4, max = 25)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords don\'t match')
		])
	confirm = PasswordField('Confirm Password')

class ArticleForm(Form):
	title = StringField('title', [validators.length(min = 1, max = 50)])
	body = TextAreaField('body')