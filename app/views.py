from app import app
from flask import render_template, g, request
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


@app.route('/', methods=['GET'])
def index():
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


@app.route('/user/<username>', methods=['GET'])
def user(username):
    '''
    CREATE TABLE "users" ( `strikes` INTEGER NOT NULL DEFAULT 0, `username` TEXT NOT NULL UNIQUE )
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select * from users where username=' + '"' + username + '"')
    user_info = list(cursor.fetchone())
    strikes, username = user_info
    return render_template("user.html", username=username, strikes=strikes)
