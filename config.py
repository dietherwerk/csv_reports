import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost/tnt_reports'

UPLOAD_FOLDER = os.path.join(basedir, 'csv_upload/')
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
