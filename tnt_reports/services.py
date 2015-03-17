from config import PAID_USER_MIN_QUOTA
from .models import Data, CSVFile


class Dataset_csv(object):

    def get_one_report(self, id):
        return CSVFile.query.get(id)

    def get_report_data(self, report_id):
        return Data.query.filter(Data.report_id == report_id)

    def get_paid_users(self, report_id):
        query = self.get_report_data(report_id)
        return query.filter(Data.quota >= PAID_USER_MIN_QUOTA)

    def get_free_users(self, report_id):
        query = self.get_report_data(report_id)
        return query.filter(Data.quota < PAID_USER_MIN_QUOTA)

    def get_paid_users_by_partner(self, report_id, partner):
        query = self.get_paid_users(report_id)
        return query.filter(Data.partner == partner)

    def get_free_users_by_partner(self, report_id, partner):
        query = self.get_free_users(report_id)
        return query.filter(Data.partner == partner)

    def get_free_users_with_used_quota(self, report_id, partner):
        query = self.get_free_users_by_partner(report_id)
        return query.filter(Data.total_quota_usage > 0)

    def get_free_users_without_used_quota(self, report_id, partner):
        query = self.get_free_users_by_partner(report_id)
        return query.filter(Data.total_quota_usage <= 0)

    def get_free_users_with_used_quota_by_partner(self, report_id, partner):
        query = self.get_free_users_by_partner(report_id, partner)
        return query.filter(Data.total_quota_usage > 0)

    def get_free_users_without_used_quota_by_partner(self, report_id, partner):
        query = self.get_free_users_by_partner(report_id, partner)
        return query.filter(Data.total_quota_usage <= 0)

    def get_total_usage(self, query):
        total_usage = 0
        for i in query:
            total_usage = total_usage + i.total_quota_usage
        return total_usage

    def get_usage_from_paid_users(self, report_id):
        query = self.get_paid_users(report_id)
        return self.get_total_usage(query)

    def get_usage_from_free_users(self, report_id):
        query = self.get_free_users(report_id)
        return self.get_total_usage(query)

    def get_usage_from_paid_users_by_partner(self, report_id, partner):
        query = self.get_paid_users_by_partner(report_id, partner)
        return self.get_total_usage(query)

    def get_usage_from_free_users_by_partner(self, report_id, partner):
        query = self.get_free_users_by_partner(report_id, partner)
        return self.get_total_usage(query)


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

