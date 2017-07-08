from app import app
from flask import Flask, render_template, g, request, flash, redirect, url_for
from .forms import LoginForm, SearchForm, UserRateSubmissionsForm, StoreRateSubmissionsForm
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
    store_uuid, latitude, longitude, display_name, strikes, username, password = row_store_info

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
    form = StoreRateSubmissionsForm(request.form)

    if form.validate_on_submit():
        flash('Update received, thank you!')

        fromCurrency = request.form.get('fromCurrency')
        toCurrency = request.form.get('toCurrency')
        rate = request.form.get('rate')
        con = sqlite3.connect(app.config['DATABASE'])
        cur = con.cursor()
        cur.execute("INSERT INTO storeRateSubmissions (storeUUID, fromCurrency, toCurrency, rate) VALUES (?,?,?,?)", (store_uuid, fromCurrency, toCurrency, rate))
        con.commit()
        con.close()
        time.sleep(2)
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
    error = None
    db = get_db()
    cursor = db.cursor()
    result = cursor.execute('SELECT * FROM users')

    if request.method == 'POST':
        for row in result:
            r = list(row)

            if request.form['username'] == r[1]: #or request.form['password'] != pwd:
                return redirect(url_for('index'))

        error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


# SEARCH PAGE
@app.route('/search', methods=['POST'])
def search():
    amount = request.form.get('amount')
    fromCurrency = request.form.get('fromCurrency')
    toCurrency = request.form.get('toCurrency')
    return render_template('search.html', amount=amount, fromCurrency=fromCurrency, toCurrency=toCurrency)
