from app import app
from flask import Flask, Response, render_template, g, request, flash, redirect, url_for
from flask.ext.login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
from .forms import LoginForm, SearchForm, UserRateSubmissionsForm, UserAddStoreForm
from .login import *
import sqlite3
import time


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


# HOMEPAGE
# The two route decorators above the function create the mappings from URLs / and /index to this function
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # returns a string, to be displayed on the client's web browser.
    form = SearchForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            redirect(url_for('search'))
    return render_template("index.html", title='Home', form=form)


@app.route('/store/<store_id>', methods=['GET', 'POST'])
def store(store_id):

    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from stores where storeUUID=' + '"' + store_id + '"')
    row_store_info = list(cursor.fetchone())
    print(row_store_info)
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

    # instantiate UserRateSubmissionsForm object
    form = UserRateSubmissionsForm(request.form)

    if form.validate_on_submit():
        flash('Update received, thank you!')
        time.sleep(3)
        return redirect('/store/' + store_id)
        




    return render_template("store.html", store_uuid=store_uuid, latitude=latitude, longitude=longitude,
                           display_name=display_name, strikes=strikes, safety_ratings=safety_ratings,
                           user_submissions=user_submissions, store_submissions=store_submissions, form=form)


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

    
    return render_template("user.html", username=username, strikes=strikes)


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    cursor = db.cursor()
    result = cursor.execute('SELECT * FROM users')
    if request.method == 'POST':
        # return '''
        # <form action='login' method='POST'>
        # <input type='text' name='username' id='username' placeholder='username'></input>
        # <input type='password' name='pw' id='pw' placeholder='password'></input>
        # <input type='submit' name='submit'></input>
        # </form>
        # '''
        username = request.form['username']
        pw = request.form['pw']
        for row in result:
            r = list(row)
            if username == r[1] and pw == r[2]:
                user = User(username, pw)
                user.name = username
                user.id = username
                login_user(user)
                return flask.redirect(flask.url_for('index'))
        return 'Bad login'
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')

# SEARCH PAGE
@app.route('/search', methods=['POST'])
def search():
    amount = request.form.get('amount')
    fromCurrency = request.form.get('fromCurrency')
    toCurrency = request.form.get('toCurrency')
    return render_template('search.html', amount=amount, fromCurrency=fromCurrency, toCurrency=toCurrency)
