from flask import Flask
from flask_bootstrap import Bootstrap

# create Flask object
app = Flask(__name__)

Bootstrap(app)

# tell Flask to read it and use config file
app.config.from_object('config')
app.secret_key = 'super secret key'

from app import views
