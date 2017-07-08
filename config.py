# Flask extensions configurations

import os


# Security is for later
WTF_CSRF_ENABLED = False
SECRET_KEY = 'you-will-never-guess'
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'db', 'XchangeFinder.db')


OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://accounts.google.com/o/oauth2/v2/auth'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]