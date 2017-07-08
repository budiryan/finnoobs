from app import app
from flask import render_template, flash, redirect
from .forms import LoginForm


### HOMEPAGE
# The two route decorators above the function create the mappings from URLs / and /index to this function
@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
	# returns a string, to be displayed on the client's web browser. 
    return render_template("index.html", title='Home')


### LOGIN PAGE
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
