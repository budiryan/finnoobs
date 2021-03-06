from app import app
from flask import Flask, Response, render_template, g, request, flash, redirect, url_for
from flask_login import *
from .forms import LoginForm, SearchForm, UserRateSubmissionsForm, StoreRateSubmissionsForm, SignupForm, SafetyRatingsForm
from .login import *
from forex_python.converter import CurrencyRates
import sqlite3
import time
import requests



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
    store_uuid, latitude, longitude, display_name, strikes, username, password, time, image = row_store_info

    # Get the location using python's requests library
    try:
        location = requests.get('http://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude)).json()['results'][0]['formatted_address']
    except:
        location = ''

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
    cursor.execute('select username, timestamp, fromCurrency, toCurrency, rate from userRateSubmissions where storeUUID=' + store_id)
    user_submissions = list(cursor.fetchall())
    # Convert all sql objects inside the list to list format
    user_submissions = [list(u) for u in user_submissions]
    # Sort based on date
    user_submissions.sort(key=lambda r: r[0])

    # Get store's submission on its own exchange rate
    '''
    CREATE TABLE "storeRateSubmissions" ( `storeUUID` INTEGER NOT NULL, `timestamp` INTEGER NOT NULL, `fromCurrency` TEXT NOT NULL, 
                                          `toCurrency` TEXT NOT NULL, `rate` REAL NOT NULL )
    '''
    cursor.execute('select timestamp, fromCurrency, toCurrency, rate from storeRateSubmissions where storeUUID=' + store_id)
    store_submissions = list(cursor.fetchall())
    # Convert all sql objects inside the list to list format
    store_submissions = [list(s) for s in store_submissions]
    store_submissions.sort(key=lambda r:r[0], reverse=True)

    try:
        current_user.getAuthenticated()
    except:
        return render_template("storeAnon.html", store_uuid=store_uuid, latitude=latitude, longitude=longitude,
            display_name=display_name, strikes=strikes, safety_ratings=safety_ratings,
            user_submissions=user_submissions, store_submissions=store_submissions, time=time, image=image, location=location)

    if current_user.getAuthenticated():
        rating_form = SafetyRatingsForm(request.form)

        if current_user.name == username:
            form = StoreRateSubmissionsForm(request.form)
            if form.validate_on_submit():
                fromCurrency = request.form.get('fromCurrency')
                toCurrency = request.form.get('toCurrency')
                rate = request.form.get('rate')
                con = sqlite3.connect(app.config['DATABASE'])
                cur = con.cursor()
                cur.execute("INSERT INTO storeRateSubmissions (storeUUID, fromCurrency, toCurrency, rate) VALUES (?,?,?,?)", (store_uuid, fromCurrency, toCurrency, rate))
                con.commit()
                con.close()
                # Currently not showing up
                flash("Update successful. Thank you!")
                time.sleep(2)
                return redirect('/store/' + store_id)
        else:
            # instantiate UserRateSubmissionsForm object
            form = UserRateSubmissionsForm(request.form)
            if form.validate_on_submit():
                fromCurrency = request.form.get('fromCurrency')
                toCurrency = request.form.get('toCurrency')
                rate = request.form.get('rate')
                con = sqlite3.connect(app.config['DATABASE'])
                cur = con.cursor()
                cur.execute("INSERT INTO userRateSubmissions (username, storeUUID, fromCurrency, toCurrency, rate) VALUES (?,?,?,?,?)", (current_user.name, store_uuid, fromCurrency, toCurrency, rate))
                con.commit()
                con.close()
                # Currently not showing up
                flash("Update successful. Thank you!")
                time.sleep(2)
                return redirect('/store/' + store_id)

        if rating_form.validate_on_submit():
            rating = request.form.get('rating')
            con = sqlite3.connect(app.config['DATABASE'])
            cur = con.cursor()
            # temporary, will change to take routed store number
            cur.execute("INSERT INTO safetyRatings (username, rating, storeUUID) VALUES (?,?,?)", (current_user.name, rating, store_id))
            con.commit()
            con.close()
            print("store id")
            print(store_id)
            flash("Thanks for your input!")
            return redirect('/store/' + store_id)

        return render_template("store.html", store_uuid=store_uuid, latitude=latitude, longitude=longitude,
            display_name=display_name, strikes=strikes, safety_ratings=safety_ratings,
            user_submissions=user_submissions, store_submissions=store_submissions, form=form, rating_form=rating_form, time=time, image=image, location=location)
    
    else:
        return render_template("storeAnon.html", store_uuid=store_uuid, latitude=latitude, longitude=longitude,
            display_name=display_name, strikes=strikes, safety_ratings=safety_ratings,
            user_submissions=user_submissions, store_submissions=store_submissions, time=time, image=image, location=location)


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
        username = request.form['username']
        pw = request.form['pw']
        for row in result:
            r = list(row)
            if username == r[1] and pw == r[2]:
                user = User(username)
                user.name = username
                user.id = username
                login_user(user)
                return redirect(url_for('index'))
        return 'Bad login'
    return render_template("login.html", title='User', form="login")

# LOGOUT PAGE
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# SIGNUP PAGE
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        pw = request.form['pw']
        con = sqlite3.connect(app.config['DATABASE'])
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, pw))
        con.commit()
        con.close()
        try:
            logout_user()
        except:
            print("nobody logged in")
        user = User(username)
        user.name = username
        user.id = username
        login_user(user)
        return redirect(url_for('index'))

    return render_template("signup.html", form="signup")

# SEARCH PAGE
@app.route('/search', methods=['POST'])
def search():
    amount = request.form.get('amount')
    fromCurrency = request.form.get('fromCurrency')
    toCurrency = request.form.get('toCurrency')
    c = CurrencyRates()
    baseline = c.get_rate(fromCurrency, toCurrency)
    db = get_db()
    cursor = db.cursor()
    all_rows = list(cursor.execute('select * from stores').fetchall())
    all_rows = [list(row) for row in all_rows]

    # Separate query for getting the rating
    list_of_ratings = list(cursor.execute('select * from safetyRatings'))
    list_of_ratings = [list(rating) for rating in list_of_ratings]

    # Concatenate each row of all the stores with averaged rating
    for index, row in enumerate(all_rows):
        count = 0
        rating_sum = 0
        for rating in list_of_ratings:
            if row[0] == rating[2]:
                count += 1
                rating_sum += rating[1]
        try:
            average_rating = rating_sum / float(count)
            all_rows[index].append(int(average_rating))
        except:
            all_rows[index].append(int(0))

    list_of_store_reports = list(cursor.execute('select * from storeRateSubmissions ORDER BY datetime(timestamp) DESC'))
    list_of_store_reports = [list(report) for report in list_of_store_reports]
    filtered_list_of_store_reports = []
    for index, report in enumerate(list_of_store_reports):
        # LOL only keep if the store has the exchange rate which was required
        if fromCurrency == report[2] and toCurrency == report[3]:
            filtered_list_of_store_reports.append(report)

    filtered_all_rows = []
    for index, report in enumerate(filtered_list_of_store_reports):
        for row in all_rows:
            if report[0] == row[0]:
                filtered_all_rows.append(row + report[1:])

    for index, row in enumerate(filtered_all_rows): 
        try:
            location = requests.get('http://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(row[1]) + ',' + str(row[2])).json()['results'][0]['formatted_address']
            time.sleep(1)
            filtered_all_rows[index].append(location)
        except:
            location = ''

    # Format: Store ID, displayName, avg_rating, fromCurrency, toCurrency, rate
    print('Your results with rates entered by stores, sorted by last update:')
    print(filtered_all_rows)

    list_of_user_reports = list(cursor.execute('select storeUUID, timestamp, fromCurrency, toCurrency, rate from userRateSubmissions ORDER BY datetime(timestamp) DESC'))
    list_of_user_reports = [list(report) for report in list_of_user_reports]
    filtered_list_of_user_reports = []
    for index, report in enumerate(list_of_user_reports):
        # LOL only keep if the store has the exchange rate which was required
        if fromCurrency == report[2] and toCurrency == report[3]:
            filtered_list_of_user_reports.append(report)

    filtered_user_rows = []
    for index, report in enumerate(filtered_list_of_user_reports):
        for row in all_rows:
            if report[0] == row[0]:
                filtered_user_rows.append(row + report[1:])

    for index, row in enumerate(filtered_user_rows): 
        try:
            location = requests.get('http://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(row[1]) + ',' + str(row[2])).json()['results'][0]['formatted_address']
            time.sleep(1)
            filtered_user_rows[index].append(location)
        except:
            location = ''

    # Format: Store ID, displayName, avg_rating, fromCurrency, toCurrency, rate
    print('Your results with rates entered by users, sorted by last update:')
    print(filtered_user_rows)

    # Assuming the store has it, user report database SHOULD also have the same transaction type
    return render_template('search.html', amount=amount, fromCurrency=fromCurrency, toCurrency=toCurrency, 
                           filtered_all_rows=filtered_all_rows, filtered_user_rows=filtered_user_rows, baseline=baseline)
