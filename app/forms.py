from flask_wtf import Form
from wtforms import StringField, BooleanField, IntegerField, SelectField, DecimalField
# DataRequired validator simply checks that the field is not submitted empty
from wtforms.validators import DataRequired

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class SearchForm(Form):
    #timestamp
    amount = DecimalField('amount', validators=[DataRequired()])
    fromCurrency = SelectField(u'from currency', choices=[('RMB', 'RMB'), ('USD', 'USD'), ('EUR', 'EUR'), ('HKD', 'HKD'), ('SGD', 'SGD')], validators=[DataRequired()])
    toCurrency =  SelectField(u'to currency', choices=[('RMB', 'RMB'), ('USD', 'USD'), ('EUR', 'EUR'), ('HKD', 'HKD'), ('SGD', 'SGD')], validators=[DataRequired()])

class UserRateSubmissionsForm(Form):
	fromCurrency = SelectField(u'from currency', choices=[('RMB', 'RMB'), ('USD', 'USD'), ('EUR', 'EUR'), ('HKD', 'HKD'), ('SGD', 'SGD')], validators=[DataRequired()])
	toCurrency =  SelectField(u'to currency', choices=[('RMB', 'RMB'), ('USD', 'USD'), ('EUR', 'EUR'), ('HKD', 'HKD'), ('SGD', 'SGD')], validators=[DataRequired()])
	rate = DecimalField('exchange rate', validators=[DataRequired()])

class StoreRateSubmissionsForm(Form):
	fromCurrency = SelectField(u'from currency', choices=[('RMB', 'RMB'), ('USD', 'USD'), ('EUR', 'EUR'), ('HKD', 'HKD'), ('SGD', 'SGD')], validators=[DataRequired()])
	toCurrency =  SelectField(u'to currency', choices=[('RMB', 'RMB'), ('USD', 'USD'), ('EUR', 'EUR'), ('HKD', 'HKD'), ('SGD', 'SGD')], validators=[DataRequired()])
	rate = DecimalField('exchange rate', validators=[DataRequired()])
