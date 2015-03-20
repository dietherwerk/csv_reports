# coding: utf-8
# Python Import
import os
from datetime import datetime
import pandas
import threading
import time

# App Import
from . import db
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
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
    dataframe = pandas.read_csv(os.path.join(UPLOAD_FOLDER, filename), sep=',')
    dataframe.fillna(value='')

    csvfile = CSVFile.query.get(csvfile_id)
    csvfile.processed_rows = 0
    csvfile.state = u'Processando'
    csvfile.total_rows = len(dataframe.index) - 1
    db.session.add(csvfile)
    db.session.commit()

    for row in xrange(len(dataframe.index)):
        create_data(dataframe, row, csvfile.id)

    db.session.add(csvfile)
    db.session.commit()


def verify_importing(report_id, thread):
    csvfile = CSVFile.query.get(report_id)
    while thread.isAlive():
        time.sleep(90)
        print 'tentativa'
    else:
        if csvfile.processed_rows >= csvfile.total_rows:
            csvfile.state = u'Sucesso'
        else:
            csvfile.state = u'Falhou'
        db.session.add(csvfile)
        db.session.commit()
        print 'ok'
    return


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_data(dataframe, row, csvfile_id):
    # Date format in reports: 2015-01-29 00:00:00.0
    string_for_convert_date = '%Y-%m-%d %H:%M:%S.%f'
    data = Data()

    data.customer_extref = dataframe['Subscription: Customer Ext Ref'][row]
    data.first_use = datetime.strptime(dataframe['Subscription: First Use'][row], string_for_convert_date)
    data.created_date = datetime.strptime(dataframe['Subscription: Created Date'][row], string_for_convert_date)
    data.uuid = dataframe['user: Uuid'][row]
    data.state = int(dataframe['user: State'][row])
    data.total_quota_usage = int(dataframe['user: Total quota usage'][row])
    data.total_storage_usage = int(dataframe['user: Total storage usage'][row])
    data.object_storage_usage = int(dataframe['user: Object storage usage'][row])
    data.video_storage_usage = int(dataframe['user: Video storage usage'][row])
    data.audio_storage_usage = int(dataframe['user: Audio storage usage'][row])
    data.image_storage_usage = int(dataframe['user: Image storage usage'][row])
    data.document_storage_usage = int(dataframe['user: Document storage usage'][row])
    data.quota = int(dataframe['user: Quota'][row])
    data.malware_count = int(dataframe['user: Total malware count'][row])
    data.total_file_count = int(dataframe['user: Total file count'][row])
    data.object_file_count = int(dataframe['user: Object file count'][row])
    data.video_file_count = int(dataframe['user: Video file count'][row])
    data.audio_file_count = int(dataframe['user: Audio file count'][row])
    data.image_file_count = int(dataframe['user: Image file count'][row])
    data.document_file_count = int(dataframe['user: Document file count'][row])
    data.trash_file_count = int(dataframe['user: Trash file count'][row])
    data.last_seen = datetime.strptime(dataframe['user: Last seen date'][row], string_for_convert_date)
    data.total_share_count = int(dataframe['user: Total share count'][row])
    data.csvfile_id = csvfile_id

    # TODO: Refactor using Regex
    no_digits = []
    for i in dataframe['Subscription: Customer Ext Ref'][row]:
        if not i.isdigit():
            no_digits.append(i)
    result = ''.join(no_digits)
    result = result.replace('-', '').replace('sync', '')
    data.partner = result

    # dataframe['Safe Avenue: Ext Ref'][row]
    # dataframe['Safe Avenue: License size'][row]
    # dataframe['Subscription: Customer Ext Ref'][row]
    # dataframe['Subscription: First Use'][row]
    # dataframe['Subscription: Created Date'][row]
    # dataframe['user: Uuid'][row]
    # int(dataframe['user: State'][row])
    # int(dataframe['user: Total quota usage'][row])
    # int(dataframe['user: Total storage usage'][row])
    # int(dataframe['user: Object storage usage'][row])
    # int(dataframe['user: Video storage usage'][row])
    # int(dataframe['user: Audio storage usage'][row])
    # int(dataframe['user: Image storage usage'][row])
    # int(dataframe['user: Document storage usage'][row])
    # int(dataframe['user: Quota'][row])
    # int(dataframe['user: Total malware count'][row])
    # int(dataframe['user: Total file count'][row])
    # int(dataframe['user: Object file count'][row])
    # int(dataframe['user: Video file count'][row])
    # int(dataframe['user: Audio file count'][row])
    # int(dataframe['user: Image file count'][row])
    # int(dataframe['user: Document file count'][row])
    # int(dataframe['user: Trash file count'][row])
    # dataframe['user: Last seen date'][row]
    # int(dataframe['user: Total share count'][row])

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
