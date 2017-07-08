from app import app
from flask import render_template, g, request, flash, redirect
from .forms import LoginForm, UserRateSubmissionsForm, UserAddStoreForm
import sqlite3


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# HOMEPAGE
# The two route decorators above the function create the mappings from URLs / and /index to this function
@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
	# returns a string, to be displayed on the client's web browser. 
    return render_template("index.html", title='Home')


@app.route('/store/<store_id>', methods=['GET', 'POST'])
def store(store_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from stores where storeUUID=' + store_id)
    row_store_info = list(cursor.fetchone())
    store_uuid, latitude, longitude, display_name, strikes = row_store_info

    # Get user's rating (format: username, rating, store_uuid, timestamp)
    cursor.execute('select username, rating, timestamp from safetyRatings where storeUUID=' + store_id)
    safety_ratings = list(cursor.fetchall())
    # Convert all sql objects inside the list to list format
    safety_ratings = [list(s) for s in safety_ratings]

    # TODO: Do average rating, and prevent same user from voting more than 1 TIME

    # Get user's submission on the store's exchange rate
    '''
    CREATE TABLE "userRateSubmissions" ( `username` TEXT NOT NULL, `storeUUID` INTEGER NOT NULL, `timestamp` INTEGER NOT NULL, 
                                         `fromCurrency` TEXT NOT NULL, `toCurrency` TEXT NOT NULL, `rate` REAL NOT NULL )
    '''
    cursor.execute('select username, timestamp, fromCurrency, toCurrency, rate from userRateSubmissions')
    user_submissions = list(cursor.fetchall())
    # Convert all sql objects inside the list to list format
    user_submissions = [list(u) for u in user_submissions]

    # Get store's submission on its own exchange rate
    '''
    CREATE TABLE "storeRateSubmissions" ( `storeUUID` INTEGER NOT NULL, `timestamp` INTEGER NOT NULL, `fromCurrency` TEXT NOT NULL, 
                                          `toCurrency` TEXT NOT NULL, `rate` REAL NOT NULL )
    '''
    cursor.execute('select timestamp, fromCurrency, toCurrency, rate from storeRateSubmissions')
    store_submissions = list(cursor.fetchall())
    # Convert all sql objects inside the list to list format
    store_submissions = [list(s) for s in store_submissions]

    return render_template("store.html", store_uuid=store_uuid, latitude=latitude, longitude=longitude,
                           display_name=display_name, strikes=strikes, safety_ratings=safety_ratings,
                           user_submissions=user_submissions, store_submissions=store_submissions)


@app.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    '''
    CREATE TABLE "users" ( `strikes` INTEGER NOT NULL DEFAULT 0, `username` TEXT NOT NULL UNIQUE )
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from users where username=' + '"' + username + '"')
    user_info = list(cursor.fetchone())
    print(user_info)
    strikes, username, password = user_info

    # instantiate UserRateSubmissionsForm object
    form = UserRateSubmissionsForm()

    if form.validate_on_submit():
        flash('Update received for store "%s", thank you!' %
              (form.displayName.data))
        return redirect('/user/<username>')

    return render_template("user.html", username=username, strikes=strikes, form=form)


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
	# instantiate LoginForm object
    form = LoginForm()
    # validate_on_submit returns true
    # - a form submission request
    # - if all the validators attached to fields are all right
    # indicating that the data is valid and can be processed
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    # send LoginForm object down to the template login.html
    return render_template('login.html', 
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])
