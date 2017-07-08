from flask_wtf import Form
from wtforms import StringField, BooleanField
# DataRequired validator simply checks that the field is not submitted empty
from wtforms.validators import DataRequired

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)