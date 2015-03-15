import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/tnt_reports'

UPLOAD_FOLDER = os.path.join(basedir, 'csv_upload/')
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

SECRET_KEY = 'BDB5DA4AFA58E76F51C8F5CD4794B'

PARTNERS = {
    'telcelmx',
    'claroar',
    'clarobr',
    'clarocl',
    'claroco',
    'clarocr',
    'clarodo',
    'claroec',
    'clarogt',
    'clarohn',
    'claroni',
    'claropa',
    'clarope',
    'claropr',
    'claropy',
    'clarosv',
    'clarouy',
}

PAID_USER_MIN_QUOTA = 10000000000
