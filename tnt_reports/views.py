# coding: utf-8
# Python imports
import os
from datetime import datetime

# Framework imports
from flask import request, redirect, url_for, flash, render_template
from werkzeug import secure_filename

# App imports
from . import app
from ..config import UPLOAD_FOLDER, PARTNERS
from .models import Data, Report
from .processes import allowed_file, report_register


@app.route('/', methods=['GET'])
def index():
    query = Report.query.all()
    return render_template('index.html', reports=query)


@app.route('/report/<int:id>', methods=['GET'])
def report(id):
    report = Report.query.get(id)
    progress = (float(report.processed_rows) / float(report.total_rows)) * 100
    data = report.datas.all()
    return render_template('report.html', report=report, data=data, progress=progress)


@app.route('/new_report', methods=['GET', 'POST'])
def new_report():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            report_register(filename)
            flash(u'Arquivo enviado!')
            return redirect(url_for('index'))
        else:
            flash(u'O arquivo não está no formato adequado!')
            return render_template('new_report.html')
    return render_template('new_report.html')
