# coding: utf-8

import os

# Python imports
from datetime import datetime

# Framework imports
from flask import request, redirect, url_for, flash, render_template
from werkzeug import secure_filename

# App imports
from . import app, db
from .helpers import allowed_file, assync_register
from threading import Thread
from .models import Data, Report

from config import UPLOAD_FOLDER


@app.route('/', methods=['GET'])
def index():
    query = Report.query.all()
    return render_template('index.html', reports=query)


@app.route('/new_report', methods=['GET', 'POST'])
def new_report():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            thr = Thread(target=assync_register, args=[filename])
            thr.start()
            flash(u'Arquivo enviado!')
        else:
            flash(u'O arquivo não está no formato adequado!')
        return render_template('index.html')
    return render_template('new_report.html')
