# coding: utf-8
# Python Import
import os
from datetime import datetime
import pandas
import threading
import time

# App Import
from . import db
from ..config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from .models import Data, Report


def report_register(filename):
    report = create_report(filename)
    report.processed_rows = 0
    report.state = u'Processando'
    db.session.add(report)
    db.session.commit()
    thr_import = threading.Thread(target=importing_to_bd, args=[filename, report.id])
    thr_import.start()
    thr_verify = threading.Thread(target=verify_importing, args=[report.id, thr_import])
    thr_verify.start()


def importing_to_bd(filename, report_id):
    dataframe = pandas.read_csv(os.path.join(UPLOAD_FOLDER, filename), sep='","')
    dataframe.fillna(value='')

    report = Report.query.get(report_id)
    report.processed_rows = 0
    report.state = u'Processando'
    report.total_rows = len(dataframe.index) - 1
    db.session.add(report)
    db.session.commit()

    for row in xrange(len(dataframe.index)):
        if row == 0:
            continue
        data = create_data(dataframe, row)
        report.processed_rows += 1
        db.session.add(data, report)
        db.session.commit()


def verify_importing(report_id, thread):
    print "Chamou a thread"
    report = Report.query.get(report_id)
    while thread.isAlive():
        time.sleep(45)
    else:
        if report.processed_rows >= report.total_rows:
            report.state = u'Sucesso'
        else:
            report.state = u'Falhou'
        db.session.add(report)
        db.session.commit()
    return


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_data(dataframe, row):
    # Date format in reports: 2015-01-29 00:00:00.0
    string_for_convert_date = '%Y-%m-%d %H:%M:%S.%f'
    data = Data()
    first_column = dataframe.iloc[row, 0].split(',')
    data.customer_extref = first_column[0].replace('"', '')
    data.first_use = datetime.strptime(first_column[1].replace('"', ''), string_for_convert_date)
    data.created_date = datetime.strptime(dataframe.iloc[row, 1].replace('"', ''), string_for_convert_date)
    data.uuid = dataframe.iloc[row, 2].replace('"', '')
    data.state = int(dataframe.iloc[row, 3].replace('"', ''))
    data.total_quota_usage = int(dataframe.iloc[row, 4].replace('"', ''))
    data.total_storage_usage = int(dataframe.iloc[row, 5].replace('"', ''))
    data.object_storage_usage = int(dataframe.iloc[row, 6].replace('"', ''))
    data.video_storage_usage = int(dataframe.iloc[row, 7].replace('"', ''))
    data.audio_storage_usage = int(dataframe.iloc[row, 8].replace('"', ''))
    data.image_storage_usage = int(dataframe.iloc[row, 9].replace('"', ''))
    data.document_storage_usage = int(dataframe.iloc[row, 10].replace('"', ''))
    data.quota = int(dataframe.iloc[row, 11].replace('"', ''))
    data.malware_count = int(dataframe.iloc[row, 12].replace('"', ''))
    data.total_file_count = int(dataframe.iloc[row, 13].replace('"', ''))
    data.object_file_count = int(dataframe.iloc[row, 14].replace('"', ''))
    data.video_file_count = int(dataframe.iloc[row, 15].replace('"', ''))
    data.audio_file_count = int(dataframe.iloc[row, 16].replace('"', ''))
    data.image_file_count = int(dataframe.iloc[row, 17].replace('"', ''))
    data.document_file_count = int(dataframe.iloc[row, 18].replace('"', ''))
    data.trash_file_count = int(dataframe.iloc[row, 19].replace('"', ''))
    data.last_seen = datetime.strptime(dataframe.iloc[row, 20].replace('"', ''), string_for_convert_date)
    data.total_share_count = int(dataframe.iloc[row, 21].replace('"', ''))
    # TODO: Refactor using Regex
    no_digits = []
    for i in first_column[0]:
        if not i.isdigit():
            no_digits.append(i)
    result = ''.join(no_digits)
    result = result.replace('-', '')
    data.partner = result.replace('sync', '')
    return data


def create_report(filename):
    report = Report()
    report.filename = filename
    db.session.add(report)
    db.session.commit()
    return report
