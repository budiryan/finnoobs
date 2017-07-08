from flask_wtf import Form
from wtforms import StringField, BooleanField, IntegerField, SelectField, DecimalField
# DataRequired validator simply checks that the field is not submitted empty
from wtforms.validators import DataRequired

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class UserRateSubmissionsForm(Form):
	# username
	displayName = SelectField(u'store', coerce=str, validators=[DataRequired()])
	#timestamp
	fromCurrency = SelectField(u'from currency', choices=[('RMB', 'RMB'), ('USD', 'USD'), ('EUR', 'EUR'), ('HKD', 'HKD'), ('SGD', 'SGD')], validators=[DataRequired()])
	toCurrency =  SelectField(u'to currency', choices=[('RMB', 'RMB'), ('USD', 'USD'), ('EUR', 'EUR'), ('HKD', 'HKD'), ('SGD', 'SGD')], validators=[DataRequired()])
	rate = DecimalField('exchange rate', validators=[DataRequired()])

class UserAddStoreForm(Form):
	displayName = StringField('store name', validators=[DataRequired()])
	latitude = DecimalField('latitude', validators=[DataRequired()])
	longitude = DecimalField('longitude', validators=[DataRequired()])

