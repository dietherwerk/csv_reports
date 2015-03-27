# Python imports
from datetime import datetime

# App imports
from . import db


class CSVFile(db.Model):
    __tablename__ = 'csvfile'
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, index=True, default=datetime.now)
    updated_date = db.Column(db.DateTime, nullable=True)
    filename = db.Column(db.String(255))
    reference_month = db.Column(db.Integer)
    reference_year = db.Column(db.Integer)
    market = db.Column(db.String(30))
    processed_rows = db.Column(db.Integer)
    total_rows = db.Column(db.Integer)
    state = db.Column(db.String(30))

# States on Safe Avenue API
# 1 - ????
# 2 - VALID
# 3 - ????
# 4 - SUSPEND


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, index=True, default=datetime.now)
    updated_date = db.Column(db.DateTime, nullable=True)
    reference_year = db.Column(db.Integer)
    reference_month = db.Column(db.Integer)
    state = db.Column(db.String(30))
    datas = db.relationship('ReportData', backref='reportdatas', lazy='dynamic')


class ReportData(db.Model):
    __tablename__ = 'reportdata'
    id = db.Column(db.Integer, primary_key=True)
    partner = db.Column(db.String(255))
    total_users = db.Column(db.BigInteger)
    free_users = db.Column(db.BigInteger)
    paid_users = db.Column(db.BigInteger)
    free_users_no_comsumption = db.Column(db.BigInteger)
    free_users_with_comsumption = db.Column(db.BigInteger)
    storage_used = db.Column(db.BigInteger)
    range_between_1 = db.Column(db.BigInteger)
    range_between_2 = db.Column(db.BigInteger)
    range_between_3 = db.Column(db.BigInteger)
    range_between_4 = db.Column(db.BigInteger)
    range_between_5 = db.Column(db.BigInteger)
    range_between_6 = db.Column(db.BigInteger)
    inactives_on_period = db.Column(db.BigInteger)
    acquisition_on_period = db.Column(db.BigInteger)
    regular_users = db.Column(db.BigInteger)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))

    report = db.relationship(Report, foreign_keys=report_id, backref="Report")
