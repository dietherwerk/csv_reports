# coding: utf-8
# Python Import
import os
from datetime import datetime
import pandas as pd

# App Import
from . import db
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, PARTNERS
from .models import CSVFile, ReportData, Report


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
    db.session.add(report)
    db.session.commit()


def remove_data_from_report(report):
    reportdata = ReportData.query.filter(ReportData.report_id == report.id)
    db.session.delete(reportdata)
    db.session.commit()


def create_report_data(reference_year, reference_month):
    csvfiles = CSVFile.query.filter(CSVFile.reference_month == reference_month and CSVFile.reference_year == reference_year)

    filename_br = csvfiles.filter(CSVFile.market == 'Brasil').first().filename
    filename_mx = csvfiles.filter(CSVFile.market == 'México').first().filename
    filename_lt = csvfiles.filter(CSVFile.market == 'Latam').first().filename
    filename_tt = csvfiles.filter(CSVFile.market == 'Titans').first().filename

    if filename_br and filename_mx and filename_lt and filename_tt:
        report = create_edit_report(reference_year, reference_month)
        change_report_state(report, 'Processando')
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
        bd_sync = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename_tt), sep=',')

        # Concatenar CSV's
        # Parâmetro 'ignore_index' serve para que não haja repetição da indexação.
        # A função do Pandas concat() recebe sempre o valor de lista
        pieces = [dataframe_br, dataframe_lt, dataframe_mx]
        big_dataframe = pd.concat(pieces, ignore_index=True)

        # Criando as listas partner e paid.
        partner = []
        paid = []
        for row in big_dataframe['Subscription: Customer Ext Ref']:
            no_digits = []
            # TODO: Refazer usando REGEX - Criando o Partner
            for i in row:
                if not i.isdigit():
                    no_digits.append(i)
            result = ''.join(no_digits)
            result = result.replace('-', '').replace('sync', '')
            partner.append(result)
            # Buscando na base bd_sync o valor do produto
            try:
                if bd_sync.loc[bd_sync['extref'] == row]['price'].iloc[0] > 0:
                    paid.append('Paid')
                else:
                    paid.append('Free')
            except:
                paid.append('Not Found')

        # Criando os ranges de utilização
        usage_quota = []
        for row in big_dataframe['user: Total quota usage']:
            if row == 0:
                usage_quota.append('Not Used')
            elif row > 0 and row < 1000000000:
                usage_quota.append('0 - 1 GB')
            elif row >= 1000000000 and row < 2000000000:
                usage_quota.append('1 - 2 GB')
            elif row >= 2000000000 and row < 3000000000:
                usage_quota.append('2 - 3 GB')
            elif row >= 3000000000 and row < 4000000000:
                usage_quota.append('3 - 4 GB')
            elif row >= 4000000000 and row < 5000000000:
                usage_quota.append('4 - 5 GB')
            else:
                usage_quota.append('5 GB or more')

        # Recebendo valor da função para comparações de Data.
        month = reference_month
        year = reference_year
        # String formatada para converter string em datetype
        string_for_convert_date = '%Y-%m-%d %H:%M:%S.%f'

        # Criando a coluna de aquisição, se for no mês corrente ele valida como True
        acquisition_this_month = []
        for row in big_dataframe['Subscription: Created Date']:
            acquisition_date = datetime.strptime(row, string_for_convert_date)
            if acquisition_date.month == month and acquisition_date.year == year:
                acquisition_this_month.append(True)
            else:
                acquisition_this_month.append(False)

        # Criando a coluna de regular_user, se for no mês corrente ele valida como True
        regular_user = []
        for row in big_dataframe['user: Last seen date']:
            last_seen_date = datetime.strptime(row, string_for_convert_date)
            if last_seen_date.month == month and acquisition_date.year == year:
                regular_user.append(True)
            else:
                regular_user.append(False)

        # TODO: Refazer usando função e map.
        # TODO: Refazer com a coluna de data de cancelamento.

        # Transformando retornos em séries de Pandas
        ps = pd.Series(partner)
        pp = pd.Series(paid)
        uq = pd.Series(usage_quota)
        am = pd.Series(acquisition_this_month)
        ru = pd.Series(regular_user)

        # Criando as colunas através das séries criadas
        big_dataframe['Partner'] = ps
        big_dataframe['Paid'] = pp
        big_dataframe['Usage Quota'] = uq
        big_dataframe['Acquisition this Month'] = am
        big_dataframe['Regular User'] = ru

        # Criando os registros no modelo

        for partner in PARTNERS:
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
            reportdata.acquisition_on_period = int(acquisition_on_this_month['Partner'].count())
            reportdata.regular_users = int(regular_users['Partner'].count())
            reportdata.report_id = report.id
            db.session.add(reportdata)
            db.session.commit()
        change_report_state(report, 'Sucesso')
    else:
        change_report_state(report, 'Erro')
