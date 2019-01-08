# -*- coding: utf-8 -*-

"""Default options for the application.
"""
import os

DEBUG = False

SESSION_TIMEOUT = 3600  # 1 Hour

HASH_KEY = ''
VALIDATE_KEY = ''
ENCRYPT_KEY = ''
SECRET_KEY = ''

PAGE_LIMIT = 25

SMS_OFFSET_TIME = 5
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def absolute(path):
    """Get the absolute path of the given file/folder.

    ``path``: File or folder.
    """
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(PROJECT_DIR, path))

config = {
    'db_name': 'temba',
    'db_host': 'localhost',
    'db_user': '',
    'db_passwd': '',
    'db_port': '5432',
    'logfile': '/tmp/fcapp-web.log',


    'smsurl': 'http://localhost:13013/cgi-bin/sendsms?username=foo&password=bar',
    'default_api_uri': 'http://localhost:8000/api/v2/contacts.json',
    'api_token': 'c8cde9dbbdda6f544018e9321d017e909b28ec51',
    'api_url': 'http://localhost:8000/api/v2/',
    'prebirth_campaign': '',
    'postbirth_campaign': '',
    'familyconnect_uri': 'http://localhost:8000/',
    'babytrigger_flow_uuid': 'ea3ddc42-9224-42ad-b4bc-14b62242d6c6'
}

try:
    from local_settings import *
except ImportError:
    pass
