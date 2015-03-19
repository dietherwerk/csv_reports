# coding: utf-8
# Python Import
import os
from datetime import datetime
import pandas
import threading
import time

# App Import
from . import db
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, CSVFORMAT_LIST
from .models import Data, CSVFile


def report_register(filename, reference_month, reference_year, market):
    csvfile = create_report(filename, reference_month, reference_year, market)
    csvfile.processed_rows = 0
    csvfile.state = u'Processando'
    db.session.add(csvfile)
    db.session.commit()
    thr_import = threading.Thread(target=importing_to_bd, args=[filename, csvfile.id])
    thr_import.start()
    thr_verify = threading.Thread(target=verify_importing, args=[csvfile.id, thr_import])
    thr_verify.start()


def importing_to_bd(filename, csvfile_id):
    dataframe = pandas.read_csv(os.path.join(UPLOAD_FOLDER, filename), sep='","')
    dataframe.fillna(value='')

    csvfile = CSVFile.query.get(csvfile_id)
    csvfile.processed_rows = 0
    csvfile.state = u'Processando'
    csvfile.total_rows = len(dataframe.index) - 1
    db.session.add(csvfile)
    db.session.commit()

    for row in xrange(len(dataframe.index)):
        if row == 0:
            continue
        create_data(dataframe, row, csvfile.id)
        csvfile.processed_rows += 1
    db.session.add(csvfile)
    db.session.commit()


def verify_importing(report_id, thread):
    csvfile = CSVFile.query.get(report_id)
    while thread.isAlive():
        time.sleep(45)
    else:
        if csvfile.processed_rows >= csvfile.total_rows:
            csvfile.state = u'Sucesso'
        else:
            csvfile.state = u'Falhou'
        db.session.add(csvfile)
        db.session.commit()
    return


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_data(dataframe, row, csvfile_id):
    # Date format in reports: 2015-01-29 00:00:00.0
    string_for_convert_date = '%Y-%m-%d %H:%M:%S.%f'
    data = Data()

    # Remove quotes
    for column in xrange(len(dataframe.columns)):
        dataframe.iloc[row, column] = dataframe.iloc[row, column].replace('"', '')

    first_column = dataframe.iloc[row, 0].split(',')
    data.customer_extref = first_column[0]
    data.first_use = datetime.strptime(first_column[1], string_for_convert_date)
    data.created_date = datetime.strptime(dataframe.iloc[row, 1], string_for_convert_date)
    data.uuid = dataframe.iloc[row, 2]
    data.state = int(dataframe.iloc[row, 3])
    data.total_quota_usage = int(dataframe.iloc[row, 4])
    data.total_storage_usage = int(dataframe.iloc[row, 5])
    data.object_storage_usage = int(dataframe.iloc[row, 6])
    data.video_storage_usage = int(dataframe.iloc[row, 7])
    data.audio_storage_usage = int(dataframe.iloc[row, 8])
    data.image_storage_usage = int(dataframe.iloc[row, 9])
    data.document_storage_usage = int(dataframe.iloc[row, 10])
    data.quota = int(dataframe.iloc[row, 11])
    data.malware_count = int(dataframe.iloc[row, 12])
    data.total_file_count = int(dataframe.iloc[row, 13])
    data.object_file_count = int(dataframe.iloc[row, 14])
    data.video_file_count = int(dataframe.iloc[row, 15])
    data.audio_file_count = int(dataframe.iloc[row, 16])
    data.image_file_count = int(dataframe.iloc[row, 17])
    data.document_file_count = int(dataframe.iloc[row, 18])
    data.trash_file_count = int(dataframe.iloc[row, 19])
    data.last_seen = datetime.strptime(dataframe.iloc[row, 20], string_for_convert_date)
    data.total_share_count = int(dataframe.iloc[row, 21])
    data.csvfile_id = csvfile_id

    # TODO: Refactor using Regex
    no_digits = []
    for i in first_column[0]:
        if not i.isdigit():
            no_digits.append(i)
    result = ''.join(no_digits)
    result = result.replace('-', '').replace('sync', '')
    data.partner = result

    db.session.add(data)


def create_report(filename, reference_month, reference_year, market):
    csvfile = CSVFile()
    csvfile.filename = filename
    csvfile.reference_month = reference_month
    csvfile.reference_year = reference_year
    csvfile.market = market
    db.session.add(csvfile)
    db.session.commit()
    return csvfile


def delete_csv(csvfile_id):
    csvfile = CSVFile.query.get(csvfile_id)
    csvfile.state = u'Processando Exclusão'
    db.session.add(csvfile)
    db.session.commit()
    thr_exclude = threading.Thread(target=delete_process, args=[csvfile_id])
    thr_verify = threading.Thread(target=verify_delete, args=[csvfile_id, thr_exclude])
    thr_exclude.start()
    thr_verify.start()


def delete_process(csvfile_id):
    csvfile = CSVFile.query.get(csvfile_id)
    Data.query.filter(Data.csvfile_id == csvfile.id).delete()
    db.session.delete(csvfile)
    db.session.commit()


def verify_delete(report_id, thread):
    while thread.isAlive():
        time.sleep(10)
    else:
        if CSVFile.query.get(report_id):
            csvfile = CSVFile.query.get(report_id)
            csvfile.state = u'Erro na Exclusão'
            db.session.add(csvfile)
            db.session.commit()
    return
