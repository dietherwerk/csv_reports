# coding: utf-8

# Framework Imports
from flask_wtf import Form
from wtforms import SelectField, FileField
from wtforms.validators import Required

# App Imports
from .helpers import dict_as_list_of_tuples, generate_year_dict, generate_month_dict, generate_market_dict


class ReportForm(Form):
    reference_month = SelectField(u'Mês', [Required()], choices=dict_as_list_of_tuples(generate_month_dict()))
    reference_year = SelectField(u'Ano', [Required()], choices=dict_as_list_of_tuples(generate_year_dict()))
    market = SelectField(u'Mercado', [Required()], choices=dict_as_list_of_tuples(generate_market_dict()))
    csv = FileField(u'Aquivo CSV', [Required()])
