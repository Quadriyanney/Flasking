from flask import Flask, session, flash, request, render_template, url_for, redirect, jsonify
from db_model import User, Article
from forms import RegisterForm, ArticleForm
from passlib.hash import sha256_crypt
from flask_pymongo import PyMongo
import time
from functools import wraps


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'flasking_db'

mongo = PyMongo(app)


#HOME PAGE
@app.route('/')
def index():
	return render_template('index.html')


#REGISTER
@app.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegisterForm(request.form)

	if request.method == 'POST' and form.validate():

		first_name = form.first_name.data
		last_name = form.last_name.data
		username = form.username.data
		email = form.email.data
		password = sha256_crypt.encrypt(str(form.password.data))

		User((mongo.db.user.count() + 1), email, username, first_name, last_name, password).save()

		return redirect(url_for('login'))

	return render_template('register.html', form = form)


#LOGIN
@app.route('/login', methods = ['GET', 'POST'])
def login():
	collection_users = mongo.db.user

	if request.method == 'POST':

		username = request.form['username']
		password = request.form['password']

		user_exists = collection_users.find_one({"username" : username})

		if user_exists:

			db_password = user_exists["password"]

			if sha256_crypt.verify(password, db_password):

				session['logged_in'] = True
				session['username'] = username
				
				return redirect(url_for('dashboard', name = username))
		
		return "<br><br><div><big>Invalid Log In details, <a href=\"{{ url_for('app.login')}}\" >Try again</a></big></div>"

	return render_template('login.html')


#DECORATOR TO CHECK IF USER IS LOGGED IN
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please Log In')
			return redirect(url_for('login'))
	return wrap


#ADD ARTICLE
@app.route('/add_article', methods = ['GET', 'POST'])
@is_logged_in
def add_article():
	form = ArticleForm(request.form)

	if request.method == 'POST' and form.validate():

		title = form.title.data
		body = form.body.data
		author = session['username']
		time_published = time.ctime()

		Article((mongo.db.article.count() + 1), title, body, author, time_published).save()

		return redirect(url_for('dashboard', name = session['username']))

	return render_template('add_article.html', form = form)


#EDIT ARTICLE
@app.route('/dashboard/edit_article/<int:article_id>', methods = ['GET', 'POST'])
@is_logged_in
def edit_article(article_id):
	collection_articles = mongo.db.article
	article =  collection_articles.find_one({"_id": article_id})
	
	form = ArticleForm(request.form)
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():

		title = request.form['title']
		body = request.form['body']

		collection_articles.update({"_id": article_id}, {'$set' : {"title": title, "body": body}})

		return redirect(url_for('dashboard', name = session['username']))

	return render_template('edit_article.html', form = form)


#DLETE ARTICLE
@app.route('/delete_article/<int:article_id>')
@is_logged_in
def delete_article(article_id):
	collection_articles = mongo.db.article
	article =  collection_articles.delete_one({"_id": article_id})
	
	return redirect(url_for('dashboard', name = session['username']))


#SHOW ALL ARTICLES
@app.route('/articles')
def articles():
	collection_articles = mongo.db.article
	articles = collection_articles.find()

	if articles:
		return render_template('articles.html', articles = articles)
	else:
		return render_template('article.html')


#SHOW ONE ARTICLE
@app.route('/article/<int:article_id>')
def article(article_id):
	collection_articles = mongo.db.article
	article =  collection_articles.find_one({"_id": article_id})

	return render_template('article.html', article = article)
	

#USER DASHBOARD
@app.route('/dashboard/<name>')
@is_logged_in
def dashboard(name):
	collection_articles = mongo.db.article
	user_articles = collection_articles.find({"author": str(name)})

	if user_articles:
		return render_template('dashboard.html', articles = user_articles)
	else:
		return render_template('dashboard.html')


#LOGOUT
@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))



if __name__=='__main__':
	app.secret_key = 'ljfdnvljdsna;/ds.lkdfkjnmkdfuworiorip324u84387932oibi23j0i3nj'
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)