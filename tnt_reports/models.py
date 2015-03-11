# Python imports
from datetime import datetime

# App imports
from . import db


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, index=True, default=datetime.now)
    updated_date = db.Column(db.DateTime, nullable=True)
    filename = db.Column(db.String(255))
    datas = db.relationship('Data', backref='datas', lazy='dynamic')


class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    customer_extref = db.Column(db.String(255))
    first_use = db.Column(db.DateTime, nullable=True)
    created_date = db.Column(db.DateTime, index=True, default=datetime.now)
    uuid = db.Column(db.String(255))
    state = db.Column(db.BigInteger)
    total_quota_usage = db.Column(db.BigInteger)
    total_storage_usage = db.Column(db.BigInteger)
    object_storage_usage = db.Column(db.BigInteger)
    video_storage_usage = db.Column(db.BigInteger)
    audio_storage_usage = db.Column(db.BigInteger)
    image_storage_usage = db.Column(db.BigInteger)
    document_storage_usage = db.Column(db.BigInteger)
    quota = db.Column(db.BigInteger)
    malware_count = db.Column(db.BigInteger)
    total_file_count = db.Column(db.BigInteger)
    object_file_count = db.Column(db.BigInteger)
    video_file_count = db.Column(db.BigInteger)
    audio_file_count = db.Column(db.BigInteger)
    image_file_count = db.Column(db.BigInteger)
    document_file_count = db.Column(db.BigInteger)
    trash_file_count = db.Column(db.BigInteger)
    last_seen = db.Column(db.DateTime, nullable=True)
    total_share_count = db.Column(db.BigInteger)
    partner = db.Column(db.String(255))
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.now)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
