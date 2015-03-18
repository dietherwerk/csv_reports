# coding: utf-8
# Python imports
import os
from datetime import datetime
from collections import OrderedDict

# Framework imports
from flask import redirect, url_for, flash, render_template
from werkzeug import secure_filename

# App imports
from . import app
from config import UPLOAD_FOLDER, PARTNERS
from .forms import ReportForm
from .models import CSVFile
from .processes import allowed_file, report_register
from .services import Dataset_report, Dataset_csv
from .helpers import delete_selection_dict, generate_month_dict, generate_year_dict


@app.route('/', methods=['GET'])
@app.route('/<int:year>', methods=['GET'])
def index(year=None):
    if not year:
        year = datetime.now().year
    query = CSVFile.query.filter(CSVFile.reference_year == year)
    months = delete_selection_dict(generate_month_dict())
    years = generate_year_dict()

    dict_numbers = {}
    dict_validation = {}
    for key, value in months.items():
        months = query.filter(CSVFile.reference_month == key)
        dict_numbers[key, value] = [
            months.filter(CSVFile.market == 'Brasil').count(),
            months.filter(CSVFile.market == 'Latam').count(),
            months.filter(CSVFile.market == 'México').count(),
            ]
        dict_validation[key, value] = [
            1,
            months.count()
            ]
    dict_numbers = OrderedDict(sorted(dict_numbers.items(), key=lambda t: t[0]))
    return render_template('index.html', year=year, years=years, numbers=dict_numbers, validation=dict_validation)


@app.route('/report/<int:year>/<int:month>', methods=['GET'])
def report(year, month):
    dataset = Dataset_report()
    data = {}
    for partner in PARTNERS:
        data[partner] = [
            dataset.get_free_users_with_used_quota_by_partner(month, year, partner).count(),
            dataset.get_free_users_without_used_quota_by_partner(month, year, partner).count(),
            dataset.get_free_users_by_partner(month, year, partner).count(),
            dataset.get_paid_users_with_used_quota_by_partner(month, year, partner).count(),
            dataset.get_paid_users_without_used_quota_by_partner(month, year, partner).count(),
            dataset.get_paid_users_by_partner(month, year, partner).count(),
        ]
    data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))
    return render_template('report.html', data=data, year=year, month=month)


@app.route('/csv', methods=['GET'])
def all_csv():
    query = CSVFile.query.all()
    return render_template('all_csv.html', csv=query)


@app.route('/csv/<int:id>', methods=['GET'])
def show_csv(id):
    report = Dataset_csv().get_one_report(id)
    progress = (float(report.processed_rows) / float(report.total_rows)) * 100
    return render_template('csv.html', report=report, progress=progress)


@app.route('/new_file', methods=['GET', 'POST'])
def new_file():
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
