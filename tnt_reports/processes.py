# coding: utf-8
# Python Import
import os
from datetime import datetime
from functools import partial
import pandas as pd

# App Import
from . import db
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, PARTNERS
from .models import CSVFile, ReportData, Report, NotFound


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def csv_register(filename, reference_month, reference_year, market):
    dataframe = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename), sep=',')
    csvfile = CSVFile()
    csvfile.filename = filename
    csvfile.reference_month = reference_month
    csvfile.reference_year = reference_year
    csvfile.market = market
    csvfile.total_rows = len(dataframe.index) - 1
    csvfile.state = u'Enviado'
    db.session.add(csvfile)
    db.session.commit()
    return csvfile


def csv_edit(csvfile_id, reference_month=None, reference_year=None, market=None):
    csvfile = CSVFile.query.get(csvfile_id)
    if reference_month:
        csvfile.reference_month = reference_month
    if reference_year:
        csvfile.reference_year = reference_year
    if market:
        csvfile.market = market
    db.session.add(csvfile)
    db.session.commit()
    return csvfile


def csv_delete(csvfile_id):
    csvfile = CSVFile.query.get(csvfile_id)
    db.session.delete(csvfile)
    db.session.commit()


def create_edit_report(year, month):
    report = Report.query.filter(Report.reference_month == month and Report.reference_year == year).first()
    if report:
        report.updated_date = datetime.utcnow()
    else:
        report = Report()
        report.reference_year = year
        report.reference_month = month
        report.state = 'Novo'
    db.session.add(report)
    db.session.commit()
    return report


def change_report_state(report, state):
    report.state = state
    report.updated_date = datetime.now()
    db.session.add(report)
    db.session.commit()


def remove_data_from_report(report):
    reportdata = ReportData.query.filter(ReportData.report_id == report.id).all()
    for data in reportdata:
        db.session.delete(data)
    db.session.delete(report)
    db.session.commit()


def create_report_data(year, month, report_id):
    csvfiles = CSVFile.query.filter(CSVFile.reference_month == month and CSVFile.reference_year == year)
    report = Report.query.get(report_id)

    filename_br = csvfiles.filter(CSVFile.market == 'Brasil').first().filename
    filename_mx = csvfiles.filter(CSVFile.market == 'México').first().filename
    filename_lt = csvfiles.filter(CSVFile.market == 'Latam').first().filename
    filename_tt = csvfiles.filter(CSVFile.market == 'Titans').first().filename

    if filename_br and filename_mx and filename_lt and filename_tt:
        dataframe_br = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename_br), sep=',')
        dataframe_mx = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename_mx), sep=',')
        dataframe_lt = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename_lt), sep=',')

        # Importando o csv extraído de SYNC
        # SELECT
        #     f.extref, u.partner, up.current_state, up.updated, p.price
        # FROM
        #     tntsync.user u
        #       JOIN
        #     tntsync.user_package up ON up.user_id = u.id
        #       JOIN
        #     tntsync.package p ON up.package_id = p.id
        #       JOIN
        #     tntsync.fsecure_migration f ON f.user_id = u.id
        # TODO: Fazer conexão direto com o banco Slave para coletar os dados.
        bd_sync = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename_tt), sep=',')

        # Concatenar CSV's
        # Parâmetro 'ignore_index' serve para que não haja repetição da indexação.
        # A função do Pandas concat() recebe sempre o valor de lista
        pieces = [dataframe_br, dataframe_lt, dataframe_mx]
        big_dataframe = pd.concat(pieces, ignore_index=True)

        # Copiar o extref para a criação do merge
        big_dataframe['extref'] = big_dataframe['Subscription: Customer Ext Ref']

        # Ordena permanecendo status active primeiro, e remove as duplicatas para merge
        bd_sync_ordered = bd_sync.sort(['current_state'], ascending=[1])
        bd_sync_no_duplicate = bd_sync_ordered.drop_duplicates(['extref'])
        big_dataframe = pd.merge(big_dataframe, bd_sync_no_duplicate, on='extref', how='left')

        # Usando map para confecção das tabelas chaves
        big_dataframe['Partner'] = map(get_partner, big_dataframe['Subscription: Customer Ext Ref'])
        big_dataframe['Usage Quota'] = map(get_range, big_dataframe['user: Total quota usage'])
        big_dataframe['Paid'] = map(get_user_type, big_dataframe['price'])
        big_dataframe['Acquisition this Month'] = map(partial(get_dates, year=year, month=month), big_dataframe['Subscription: Created Date'])
        big_dataframe['Regular User'] = map(partial(get_dates, year=year, month=month), big_dataframe['user: Last seen date'])

        # Criando os registros no modelo
        for partner in PARTNERS:
            populate_reportdata(big_dataframe, partner, report)
        populate_reportdata(big_dataframe, 'Total', report)

        change_report_state(report, 'Sucesso')
    else:
        change_report_state(report, 'Erro')


def get_partner(data):
    no_digits = []
    # TODO: Refazer usando REGEX - Criando o Partner
    for i in data:
        if not i.isdigit():
            no_digits.append(i)
    partner = ''.join(no_digits)
    partner = partner.replace('-', '').replace('sync', '')
    return partner


def get_user_type(data):
    try:
        if data > 0:
            paid = 'Paid'
        else:
            paid = 'Free'
    except:
        paid = 'Not Found'
    return paid


def get_range(data):
    if data == 0:
        usage_quota = u'Not Used'
    elif data > 0 and data < 1000000000:
        usage_quota = u'0 - 1 GB'
    elif data >= 1000000000 and data < 2000000000:
        usage_quota = u'1 - 2 GB'
    elif data >= 2000000000 and data < 3000000000:
        usage_quota = u'2 - 3 GB'
    elif data >= 3000000000 and data < 4000000000:
        usage_quota = u'3 - 4 GB'
    elif data >= 4000000000 and data < 5000000000:
        usage_quota = u'4 - 5 GB'
    else:
        usage_quota = u'5 GB or more'
    return usage_quota


def get_dates(data, year, month):
        # String formatada para converter string em datetype
        string_for_convert_date = '%Y-%m-%d %H:%M:%S.%f'
        data = datetime.strptime(data, string_for_convert_date)
        if data.month == month and data.year == year:
            data = True
        else:
            data = False
        return data


def populate_reportdata(big_dataframe, partner, report):
    if partner == 'Total':
        partnered = big_dataframe
    else:
        partnered = big_dataframe[(big_dataframe['Partner'] == partner)]
    active_users = partnered[(partnered['user: State'] == 2)]
    free_users = active_users[(active_users['Paid'] == 'Free')]
    paid_users = active_users[(active_users['Paid'] == 'Paid')]
    free_users_no_comsumption = free_users[(free_users['user: Total quota usage'] == 0)]
    free_users_with_comsumption = free_users[(free_users['user: Total quota usage'] > 0)]
    storage_used = active_users['user: Total quota usage']
    range_0_1 = free_users[(free_users['Usage Quota'] == '0 - 1 GB')]
    range_1_2 = free_users[(free_users['Usage Quota'] == '1 - 2 GB')]
    range_2_3 = free_users[(free_users['Usage Quota'] == '2 - 3 GB')]
    range_3_4 = free_users[(free_users['Usage Quota'] == '3 - 4 GB')]
    range_4_5 = free_users[(free_users['Usage Quota'] == '4 - 5 GB')]
    range_5 = free_users[(free_users['Usage Quota'] == '5 GB or more')]
    acquisition_on_this_month = active_users[(active_users['Acquisition this Month'] == True)]
    regular_users = active_users[(active_users['Regular User'] == True)]

    reportdata = ReportData()
    reportdata.partner = partner
    reportdata.total_users = int(active_users['Partner'].count())
    reportdata.free_users = int(free_users['Partner'].count())
    reportdata.paid_users = int(paid_users['Partner'].count())
    reportdata.free_users_no_comsumption = int(free_users_no_comsumption['Partner'].count())
    reportdata.free_users_with_comsumption = int(free_users_with_comsumption['Partner'].count())
    reportdata.storage_used = int(storage_used.sum())
    reportdata.range_between_1 = int(range_0_1['Partner'].count())
    reportdata.range_between_2 = int(range_1_2['Partner'].count())
    reportdata.range_between_3 = int(range_2_3['Partner'].count())
    reportdata.range_between_4 = int(range_3_4['Partner'].count())
    reportdata.range_between_5 = int(range_4_5['Partner'].count())
    reportdata.range_between_6 = int(range_5['Partner'].count())
    # TODO: Fazer o inactives a partir do relatório da Younited comtemplar esse.
    reportdata.inactives_on_period = 0
    reportdata.acquisition_on_period = int(acquisition_on_this_month['Partner'].count())
    reportdata.regular_users = int(regular_users['Partner'].count())
    reportdata.report_id = report.id
    db.session.add(reportdata)
    db.session.commit()
