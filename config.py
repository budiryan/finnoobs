# Flask extensions configurations

import os


# Security is for later
WTF_CSRF_ENABLED = False
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'db', 'XchangeFinder.db')
