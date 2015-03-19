import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost/tnt_reports'

UPLOAD_FOLDER = os.path.join(basedir, 'csv_upload/')
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

SECRET_KEY = 'BDB5DA4AFA58E76F51C8F5CD4794B'

PARTNERS = {
    'telcelmx',
    'claroar',
    'clarobr',
    'clarocl',
    'claroco',
    'clarocr',
    'clarodo',
    'claroec',
    'clarogt',
    'clarohn',
    'claroni',
    'claropa',
    'clarope',
    'claropr',
    'claropy',
    'clarosv',
    'clarouy',
}

CSVFORMAT_LIST = [
        'customer_extref',
        'first_use',
        'created_date',
        'uuid',
        'state',
        'total_quota_usage',
        'total_storage_usage',
        'object_storage_usage',
        'video_storage_usage',
        'audio_storage_usage',
        'image_storage_usage',
        'document_storage_usage',
        'quota',
        'malware_count',
        'total_file_count',
        'object_file_count',
        'video_file_count',
        'audio_file_count',
        'image_file_count',
        'document_file_count',
        'trash_file_count',
        'last_seen',
        'total_share_count',
        'updated_data',
        'partner',
        'csvfile_id',
    ]

PAID_USER_MIN_QUOTA = 10000000000

QUOTAS = {
    'zero': 0,
    'one': 1000000000,
    'two': 2000000000,
    'three': 3000000000,
    'four': 4000000000,
    'five': 5000000000,
}
