from .models import CSVFile


class Dataset_csv(object):

    def get_one_file(self, id):
        return CSVFile.query.get(id)
