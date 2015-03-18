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

    _dataframe = pandas.DataFrame(columns=CSVFORMAT_LIST)
    for row in xrange(len(dataframe.index)):
        if row == 0:
            continue
        create_data(dataframe, row, csvfile.id, _dataframe)
        csvfile.processed_rows += 1
        db.session.add(csvfile)
        db.session.commit()
    _dataframe.to_csv(os.path.join(UPLOAD_FOLDER, filename+'copy'), sep=',')


def verify_importing(report_id, thread):
    print "Chamou a thread"
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


def create_data(dataframe, row, csvfile_id, _dataframe):
    # Date format in reports: 2015-01-29 00:00:00.0
    string_for_convert_date = '%Y-%m-%d %H:%M:%S.%f'
    data = Data()

    # Remove quotes
    for column in xrange(len(dataframe.columns)):
        dataframe.iloc[row, column] = dataframe.iloc[row, column].replace('"', '')

    first_column = dataframe.iloc[row, 0].split(',')
    # data.customer_extref = first_column[0]
    # data.first_use = datetime.strptime(first_column[1], string_for_convert_date)
    # data.created_date = datetime.strptime(dataframe.iloc[row, 1], string_for_convert_date)
    # data.uuid = dataframe.iloc[row, 2]
    # data.state = int(dataframe.iloc[row, 3])
    # data.total_quota_usage = int(dataframe.iloc[row, 4])
    # data.total_storage_usage = int(dataframe.iloc[row, 5])
    # data.object_storage_usage = int(dataframe.iloc[row, 6])
    # data.video_storage_usage = int(dataframe.iloc[row, 7])
    # data.audio_storage_usage = int(dataframe.iloc[row, 8])
    # data.image_storage_usage = int(dataframe.iloc[row, 9])
    # data.document_storage_usage = int(dataframe.iloc[row, 10])
    # data.quota = int(dataframe.iloc[row, 11])
    # data.malware_count = int(dataframe.iloc[row, 12])
    # data.total_file_count = int(dataframe.iloc[row, 13])
    # data.object_file_count = int(dataframe.iloc[row, 14])
    # data.video_file_count = int(dataframe.iloc[row, 15])
    # data.audio_file_count = int(dataframe.iloc[row, 16])
    # data.image_file_count = int(dataframe.iloc[row, 17])
    # data.document_file_count = int(dataframe.iloc[row, 18])
    # data.trash_file_count = int(dataframe.iloc[row, 19])
    # data.last_seen = datetime.strptime(dataframe.iloc[row, 20], string_for_convert_date)
    # data.total_share_count = int(dataframe.iloc[row, 21])
    # data.csvfile_id = csvfile_id

    # TODO: Refactor using Regex
    no_digits = []
    for i in first_column[0]:
        if not i.isdigit():
            no_digits.append(i)
    result = ''.join(no_digits)
    result = result.replace('-', '').replace('sync', '')

    _dataframe.loc[row] = [
        first_column[0],
        datetime.strptime(first_column[1], string_for_convert_date),
        datetime.strptime(dataframe.iloc[row, 1], string_for_convert_date),
        dataframe.iloc[row, 2],
        int(dataframe.iloc[row, 3]),
        int(dataframe.iloc[row, 4]),
        int(dataframe.iloc[row, 5]),
        int(dataframe.iloc[row, 6]),
        int(dataframe.iloc[row, 7]),
        int(dataframe.iloc[row, 8]),
        int(dataframe.iloc[row, 9]),
        int(dataframe.iloc[row, 10]),
        int(dataframe.iloc[row, 11]),
        int(dataframe.iloc[row, 12]),
        int(dataframe.iloc[row, 13]),
        int(dataframe.iloc[row, 14]),
        int(dataframe.iloc[row, 15]),
        int(dataframe.iloc[row, 16]),
        int(dataframe.iloc[row, 17]),
        int(dataframe.iloc[row, 18]),
        int(dataframe.iloc[row, 19]),
        datetime.strptime(dataframe.iloc[row, 20], string_for_convert_date),
        dataframe.iloc[row, 21],
        result,
        datetime.now(),
        csvfile_id,
    ]
    # _dataframe.iloc[row] = first_column[0]
    # _dataframe.iloc[row, 1] = datetime.strptime(first_column[1], string_for_convert_date)
    # _dataframe.iloc[row, 2] = datetime.strptime(dataframe.iloc[row, 1], string_for_convert_date)
    # _dataframe.iloc[row, 3] = dataframe.iloc[row, 2]
    # _dataframe.iloc[row, 4] = int(dataframe.iloc[row, 3])
    # _dataframe.iloc[row, 5] = int(dataframe.iloc[row, 4])
    # _dataframe.iloc[row, 6] = int(dataframe.iloc[row, 5])
    # _dataframe.iloc[row, 7] = int(dataframe.iloc[row, 6])
    # _dataframe.iloc[row, 8] = int(dataframe.iloc[row, 7])
    # _dataframe.iloc[row, 9] = int(dataframe.iloc[row, 8])
    # _dataframe.iloc[row, 10] = int(dataframe.iloc[row, 9])
    # _dataframe.iloc[row, 11] = int(dataframe.iloc[row, 10])
    # _dataframe.iloc[row, 12] = int(dataframe.iloc[row, 11])
    # _dataframe.iloc[row, 13] = int(dataframe.iloc[row, 12])
    # _dataframe.iloc[row, 14] = int(dataframe.iloc[row, 13])
    # _dataframe.iloc[row, 15] = int(dataframe.iloc[row, 14])
    # _dataframe.iloc[row, 16] = int(dataframe.iloc[row, 15])
    # _dataframe.iloc[row, 17] = int(dataframe.iloc[row, 16])
    # _dataframe.iloc[row, 18] = int(dataframe.iloc[row, 17])
    # _dataframe.iloc[row, 19] = int(dataframe.iloc[row, 18])
    # _dataframe.iloc[row, 20] = int(dataframe.iloc[row, 19])
    # _dataframe.iloc[row, 21] = datetime.strptime(dataframe.iloc[row, 20], string_for_convert_date)
    # _dataframe.iloc[row, 22] = dataframe.iloc[row, 21]
    # _dataframe.iloc[row, 23] = result
    # _dataframe.iloc[row, 24] = datetime.now()
    # _dataframe.iloc[row, 25] = csvfile_id


    # data.partner = result.

    return data


def create_report(filename, reference_month, reference_year, market):
    csvfile = CSVFile()
    csvfile.filename = filename
    csvfile.reference_month = reference_month
    csvfile.reference_year = reference_year
    csvfile.market = market
    db.session.add(csvfile)
    db.session.commit()
    return csvfile
