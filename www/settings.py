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
    'babytrigger_flow_uuid': 'ea3ddc42-9224-42ad-b4bc-14b62242d6c6',
    # CHWR confs
    'chwr_user': '',
    'chwr_password': '',
    'chwr_baseurl': 'http://hris.health.go.ug/iHRIS/dev/chwr/FHIR/Person/_history?_format=json'
}

# The contact fields to pull fron RapidPro
ContactFieldsToCache = [
    'lmp', 'edd', 'name', 'dob_child_1', 'dob_child_2', 'dob_child_3', 'facility', 'secreceiver_msisdn', 'hoh_msisdn',
    'last_baby_trigger', 'optout_date', 'optout_reason', 'type', 'secreceivertype', 'registered_by',
    'preferred_language', 'gender', 'uuid', 'mother_name', 'last_baby_trigger', 'self_registered',
    # mostly EMTCT ones follow
    'date_of_reprod_age_registrations', 'pregnancy_age_at_enrollment', 'fc_emtct_baby_date',
    'next_appointment_date', 'fc_emtct_next_appointment_date', 'sex', 'age_of_baby_at_enrollment',
    'last_visit_date', 'date_of_last_pregnancy_registration', 'health_facility', 'age_years',
    'encounter_type', 'date_of_last_reprod_age_registration', 'fc_emtct_pregnancy_date',
    'patient_phone_number', 'eid_number', 'trusted_person', 'dates_of_pregnancy_registrations',
    'openmrs_id', 'last_reg_date', 'birth_date'
]
PYTHON_EXECUTABLE = "/var/www/envs/fcapp/bin/python"
CONTACT_CACHE_COMMAND = PYTHON_EXECUTABLE + " " + BASE_DIR + "/contact_update_command.py"

try:
    from local_settings import *
except ImportError:
    pass
