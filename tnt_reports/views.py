# coding: utf-8
# Python imports
import os
from datetime import datetime

# Framework imports
from flask import request, redirect, url_for, flash, render_template
from werkzeug import secure_filename

# App imports
from . import app
from config import UPLOAD_FOLDER, PARTNERS
from .forms import ReportForm
from .models import Data, Report
from .processes import allowed_file, report_register
from .services import Dataset


@app.route('/', methods=['GET'])
def index():
    query = Report.query.all()
    return render_template('index.html', reports=query)


@app.route('/report/<int:id>', methods=['GET'])
def report(id):
    dataset = Dataset()
    report = dataset.get_one_report(id)
    progress = (float(report.processed_rows) / float(report.total_rows)) * 100

    data = {}
    for partner in PARTNERS:
        data[partner] = [
            dataset.get_free_users_by_partner(id, partner).count(),
            dataset.get_paid_users_by_partner(id, partner).count(),
            dataset.get_free_users_with_used_quota_by_partner(id, partner).count(),
            dataset.get_free_users_without_used_quota_by_partner(id, partner).count()
        ]


    return render_template('report.html', report=report, data=data, progress=progress)


@app.route('/new_report', methods=['GET', 'POST'])
def new_report():
    form = ReportForm()
    if form.validate_on_submit():
        file = form.csv.data
        reference_month = form.reference_month.data
        reference_year = form.reference_year.data
        market = form.market.data
        if file and allowed_file(file.filename):
            filename = secure_filename(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            report_register(filename, reference_month, reference_year, market)
            flash(u'Arquivo enviado!')
            return redirect(url_for('index'))
        else:
            flash(u'O arquivo não está no formato adequado!')
            return render_template('new_report.html', form=form)
    return render_template('new_report.html', form=form)
