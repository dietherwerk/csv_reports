# coding: utf-8
# Python imports
import os
import threading
from datetime import datetime
from collections import OrderedDict

# Framework imports
from flask import url_for, flash, render_template, request, redirect
from werkzeug import secure_filename

# App imports
from . import app
from config import UPLOAD_FOLDER
from .forms import IncludeCSVForm, RemoveCSVForm
from .models import CSVFile, Report, ReportData, NotFound
from .processes import allowed_file, csv_register, csv_delete, csv_edit, create_report_data, remove_data_from_report, create_edit_report, change_report_state
from .helpers import delete_selection_dict, generate_month_dict, generate_year_dict


@app.route('/', methods=['GET'])
@app.route('/<int:year>', methods=['GET'])
def index(year=None):
    if not year:
        year = datetime.now().year
    csvfile = CSVFile.query.filter(CSVFile.reference_year == year)
    report = Report.query.filter(Report.reference_year == year)
    months = delete_selection_dict(generate_month_dict())
    years = generate_year_dict()

    dict_numbers = {}
    dict_validation = {}
    for key, value in months.items():
        months_csv = csvfile.filter(CSVFile.reference_month == key)
        dict_numbers[key, value] = [
            months_csv.filter(CSVFile.market == 'Brasil').count(),
            months_csv.filter(CSVFile.market == 'Latam').count(),
            months_csv.filter(CSVFile.market == 'México').count(),
            months_csv.filter(CSVFile.market == 'Titans').count(),
            ]
        months_report = report.filter(Report.reference_month == key)
        dict_validation[key, value] = [
            months_report.filter(Report.state == u'Sucesso').count(),
            months_report.filter(Report.state == u'Processando').count(),
            months_csv.count()
            ]
    dict_numbers = OrderedDict(sorted(dict_numbers.items(), key=lambda t: t[0]))
    return render_template('index.html', year=year, years=years, numbers=dict_numbers, validation=dict_validation)


@app.route('/report/<int:year>/<int:month>', methods=['GET'])
def report(year, month):
    report = Report.query.filter(Report.reference_month == month and Report.reference_year == year).first()
    reportdata = ReportData.query.filter(ReportData.report_id == report.id).order_by(ReportData.partner.asc()).all()
    return render_template('report.html', report=report, reportdata=reportdata, year=year, month=month)


@app.route('/report/process/<int:year>/<int:month>', methods=['GET'])
def process(year, month):
    report = create_edit_report(year, month)
    change_report_state(report, 'Processando')
    create = threading.Thread(target=create_report_data, args=[year, month, report.id])
    create.start()
    flash(u'Relatório sendo processado!')
    return redirect(request.referrer)


@app.route('/report/remove/<int:year>/<int:month>', methods=['GET'])
def remove(year, month):
    report = Report.query.filter(Report.reference_month == month and Report.reference_year == year).first()
    remove_data_from_report(report)
    flash(u'Relatório excluído!')
    return redirect(request.referrer)


@app.route('/csv', methods=['GET'])
def all_csv():
    query = CSVFile.query.all()
    return render_template('csv_all.html', csv=query)


@app.route('/csv/show/<int:id>', methods=['GET'])
def show_csv(id):
    csv = CSVFile.query.get(id)
    return render_template('csv_show.html', report=csv)


@app.route('/csv/delete/<int:id>', methods=['GET', 'POST'])
def del_csv(id):
    csv = CSVFile.query.get(id)
    form = RemoveCSVForm()
    if form.validate_on_submit():
        csv_delete(csv.id)
        flash(u'Arquivo apagado com sucesso!')
        return redirect(url_for('all_csv'))
    return render_template('csv_delete.html', report=csv, form=form)


@app.route('/csv/new', methods=['GET', 'POST'])
def new_csv():
    form = IncludeCSVForm()
    if form.validate_on_submit():
        file = form.csv.data
        reference_month = form.reference_month.data
        reference_year = form.reference_year.data
        market = form.market.data
        if file and allowed_file(file.filename):
            filename = secure_filename(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            csv_register(filename, reference_month, reference_year, market)
            flash(u'Arquivo enviado!')
            return redirect(url_for('all_csv'))
        else:
            flash(u'O arquivo não está no formato adequado!')
            return render_template('new_report.html', form=form)
    return render_template('csv_new.html', form=form)


@app.route('/report/notfound/<int:year>/<int:month>', methods=['GET'])
def notfound(year, month):
    report = Report.query.filter(Report.reference_month == month and Report.reference_year == year).first()
    notfound = NotFound.query.filter(NotFound.report_id == report.id and NotFound.state == 2).all()
    return render_template('notfound.html', notfound=notfound, year=year, month=month)
