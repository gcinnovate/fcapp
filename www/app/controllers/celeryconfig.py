BROKER_URL = 'redis://localhost:6379/5'

db_conf = {
    'host': 'localhost',
    'name': 'fctemba',
    'user': 'postgres',
    'passwd': 'postgres',
    'port': '5432'
}

config = {
}

USE_OLD_WEBHOOK = True
# Flows and their associated flow variables. keys represent flows
INDICATORS = {
    'gis': [
        'quarter',
        'hh_number', 'male_lt_1_month', 'female_lt_1_month', 'male_1_11_month', 'female_1_11_month',
        'male_1_5_yrs', 'female_1_5_yrs', 'male_10_14_yrs', 'female_10_14_yrs', 'male_15_19_yrs',
        'female_15_19_yrs', 'male_20_24_yrs', 'female_20_24_yrs', 'male_25_49_yrs', 'female_25_49_yrs',
    ]
}

try:
    from local_celeryconfig import *
except ImportError:
    pass
