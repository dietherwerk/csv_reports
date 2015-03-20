from config import PAID_USER_MIN_QUOTA, QUOTAS
from .models import Data, CSVFile
from . import db


class Dataset_csv(object):

    def get_one_file(self, id):
        return CSVFile.query.get(id)


class Dataset_report(object):
    def get_one(self, month, year):
        return Data.query.filter(CSVFile.reference_month == month and CSVFile.reference_year == year)

    def get_active(self, month, year):
        query = self.get_one(month, year)
        return query.filter(Data.state == '2')

    def get_free_users(self, month, year):
        query = self.get_active(month, year)
        return query.filter(Data.quota < PAID_USER_MIN_QUOTA)

    def get_paid_users(self, month, year):
        query = self.get_active(month, year)
        return query.filter(Data.quota >= PAID_USER_MIN_QUOTA)

    def get_free_users_by_partner(self, month, year, partner):
        query = self.get_free_users(month, year)
        return query.filter(Data.partner == partner)

    def get_paid_users_by_partner(self, month, year, partner):
        query = self.get_paid_users(month, year)
        return query.filter(Data.partner == partner)

    def get_free_users_without_used_quota(self, month, year):
        query = self.get_free_users(month, year)
        return query.filter(Data.total_quota_usage == 0)

    def get_free_users_with_used_quota(self, month, year):
        query = self.get_free_users(month, year)
        return query.filter(Data.total_quota_usage > 0)

    def get_paid_users_without_used_quota(self, month, year):
        query = self.get_paid_users(month, year)
        return query.filter(Data.total_quota_usage == 0)

    def get_paid_users_with_used_quota(self, month, year):
        query = self.get_paid_users(month, year)
        return query.filter(Data.total_quota_usage > 0)

    def get_free_users_without_used_quota_by_partner(self, month, year, partner):
        query = self.get_free_users_by_partner(month, year, partner)
        return query.filter(Data.total_quota_usage == 0)

    def get_free_users_with_used_quota_by_partner(self, month, year, partner):
        query = self.get_free_users_by_partner(month, year, partner)
        return query.filter(Data.total_quota_usage > 0)

    def get_paid_users_without_used_quota_by_partner(self, month, year, partner):
        query = self.get_paid_users_by_partner(month, year, partner)
        return query.filter(Data.total_quota_usage == 0)

    def get_paid_users_with_used_quota_by_partner(self, month, year, partner):
        query = self.get_paid_users_by_partner(month, year, partner)
        return query.filter(Data.total_quota_usage > 0)

    def get_free_user_consumption_range(self, month, year, min_quota, max_quota):
        query = self.get_free_users(month, year)
        # import ipdb; ipdb.set_trace()
        return query.filter(db.text("total_quota_usage>:min and total_quota_usage<=:max")).params(min=min_quota, max=max_quota)
        # query.filter(Data.total_quota_usage > min_quota and Data.total_quota_usage <= max_quota)

    def get_free_user_comsumption_range_by_partner(self, month, year, partner, min_quota, max_quota):
        query = self.get_free_user_consumption_range(month, year, min_quota, max_quota)
        return query.filter(Data.partner == partner)
