# coding: utf-8
# Framework imports
from flask import Flask

# Lib imports
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from . import views
