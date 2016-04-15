"""All configuration constants"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# Database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# File upload constants
MAX_CONTENT_LENGTH = 64 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['csv'])
FILE_CREATION_FOLDER = '/tmp'

# Regular Expressions
USER_IDS_REGEX = "^\d+(,\d+)*$"
ATTRIBUTES_REGEX = "^\w+(,\w+)*$"
ALLOWED_CSV_ROW_FORMAT = "^\d+,\w+,\w+$"
