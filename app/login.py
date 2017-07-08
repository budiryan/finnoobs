from app import *
from app import views,
import flask
from flask_login import *
import sqlite3

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

	def __init__(self, name):
		self.id = name
		self.name = name

@login_manager.user_loader
def user_loader(name):
	name = request.form.get('username')
    db = get_db()
    cursor = db.cursor()
    result = cursor.execute('SELECT * FROM users')

    for row in result:
        r = list(row)
        if name == r[1]: #or pwd != r[2]:
            user = User(name)
            return user
    return


@login_manager.request_loader
def request_loader(request):
    name = request.form.get('username')
    db = get_db()
    cursor = db.cursor()
    result = cursor.execute('SELECT * FROM users')

    for row in result:
    	r = list(row)
    	if name == r[1]: #or request.form['pw'] != r[2]:
       		user.is_authenticated = request.form['pw'] == r[2]
       		user = User(name)
    		return user
    return