from app import app
from flask import render_template

# INDEX returns a string, to be displayed on the client's web browser. 
# The two route decorators above the function create the mappings from URLs / and /index to this function

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    return render_template("index.html", title='Home')
