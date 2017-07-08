from app import app
import flask
from flask.ext.login import LoginManager, UserMixin
import sqlite3
from .views import *

login_manager = LoginManager()
login_manager.init_app(app)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.commit()
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#User class
class User(UserMixin):
	def is_authenticated():
		return True

	def is_active():
		return True

	def __init__(self, name, pwd):
		self.id = name
		self.name = name
		self.pwd = pwd

@login_manager.user_loader
def user_loader(name):
    db = get_db()
    cursor = db.cursor()
    result = cursor.execute('SELECT * FROM users')

    for row in result:
        r = list(row)
        if name != r[1]: #or pwd != r[2]:
            return

    user = User(name, r[2])
    user.name = name
    user.pwd = r[2]
    return user


@login_manager.request_loader
def request_loader(request):
    name = request.form.get('name')
    if name != 'admin':
        return

    db = get_db()
    cursor = db.cursor()
    result = cursor.execute('SELECT * FROM users')

    for row in result:
    	r = list(row)
    	if request.form['name'] != r[1] or request.form['pw'] != r[2]:
       		return

    user.is_authenticated = request.form['pw'] == r[2]
    user = User(name, r[2])

    return user