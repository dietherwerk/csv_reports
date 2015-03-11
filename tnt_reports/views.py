# Python imports
import os
import csv
from datetime import datetime

# Framework imports
from flask import request, redirect, url_for
from werkzeug import secure_filename

# Config imports
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

# App imports
from . import app, db
from .models import Data, Report


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_data(row):

    # Date format in reports: 2015-01-29 00:00:00.0
    string_for_convert_date = '%Y-%m-%d %H:%M:%S.%f'

    data = Data()
    data.customer_extref = row[0]
    data.first_use = datetime.strptime(row[1], string_for_convert_date)
    data.created_date = datetime.strptime(row[2], string_for_convert_date)
    data.uuid = row[3]
    data.state = int(row[4])
    data.total_quota_usage = int(row[5])
    data.total_storage_usage = int(row[6])
    data.object_storage_usage = int(row[7])
    data.video_storage_usage = int(row[8])
    data.audio_storage_usage = int(row[9])
    data.image_storage_usage = int(row[10])
    data.document_storage_usage = int(row[11])
    data.quota = int(row[12])
    data.malware_count = int(row[13])
    data.total_file_count = int(row[14])
    data.object_file_count = int(row[15])
    data.video_file_count = int(row[16])
    data.audio_file_count = int(row[17])
    data.image_file_count = int(row[18])
    data.document_file_count = int(row[19])
    data.trash_file_count = int(row[20])
    data.last_seen = datetime.strptime(row[21], string_for_convert_date)
    data.total_share_count = int(row[22])
    no_digits = []
    for i in row[0]:
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


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            report = create_report(filename)
            with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as f:
                reader = csv.reader(f)
                totalnum = 0
                for i in reader:
                    totalnum += 1
                f.close()
            with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as f:
                rownum = 0
                reader = csv.reader(f)
                for row in reader:
                    if rownum == 0:
                        pass
                    else:
                        data = create_data(row)
                        percentage = ((float(rownum) / float(totalnum)) * 100)
                        print percentage
                        db.session.add(data, report)
                    rownum += 1
                    db.session.commit()
                f.close()
                return "OK"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
