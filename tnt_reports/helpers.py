# coding: utf-8
from collections import OrderedDict
from datetime import datetime


def generate_month_dict():
    month_dict = {
        '': u'Selecione',
        '01': u'Janeiro',
        '02': u'Fevereiro',
        '03': u'Março',
        '04': u'Abril',
        '05': u'Maio',
        '06': u'Junho',
        '07': u'Julho',
        '08': u'Agosto',
        '09': u'Setembro',
        '10': u'Outubro',
        '11': u'Novembro',
        '12': u'Dezembro'
    }
    month_dict = OrderedDict(sorted(month_dict.items(), key=lambda t: t[0]))
    return month_dict


def generate_year_dict():
    year_dict = OrderedDict()
    year_now = datetime.now().strftime('%Y')
    previous_year = str(int(year_now) - 1)
    next_year = str(int(year_now) + 1)
    year_dict[previous_year] = previous_year
    year_dict[year_now] = year_now
    year_dict[next_year] = next_year
    return year_dict


def generate_market_dict():
    market_dict = {
        '': u'Selecione',
        u'Brasil': u'Brasil',
        u'Latam': u'Latam',
        u'México': u'México',
    }
    market_dict = OrderedDict(sorted(market_dict.items(), key=lambda t: t[0]))
    return market_dict


def dict_as_list_of_tuples(selected_dict):
    selected_list = []
    for key, value in selected_dict.items():
        tupla = (key, value)
        selected_list.append(tupla)
    return selected_list
