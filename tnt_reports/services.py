from config import PAID_USER_MIN_QUOTA
from .models import Data, Report


class Dataset(object):

    def get_one_report(self, id):
        return Report.query.get(id)

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
