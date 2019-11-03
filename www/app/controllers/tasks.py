import web
import json
import psycopg2.extras
import simplejson
from celery import Celery
from celeryconfig import BROKER_URL, db_conf, INDICATORS
from utils import get_indicators_from_rapidpro_results
import datetime

MAX_CHUNK_SIZE = 90

db = web.database(
    dbn='postgres',
    user=db_conf['user'],
    pw=db_conf['passwd'],
    db=db_conf['name'],
    host=db_conf['host'],
    port=db_conf['port']
)
# celery -A tasks worker --loglevel=info
app = Celery("fcapp", broker=BROKER_URL)

allDistrictsByName = {}
rs = db.query("SELECT id, name FROM  fcapp_locations WHERE level = 2 ORDER BY name")
for r in rs:
    allDistrictsByName[r['name']] = r['id']


@app.task(name="save_flow_data")
def save_flow_data(request_args, request_json):
    msisdn = request_args.get('msisdn')
    report_type = request_args.get('report_type')
    district = request_args.get('district').title()
    subcounty = request_args.get('subcounty')
    village = request_args.get('village')
    facility = request_args.get('facility')
    facilityuid = request_args.get('facilityuid')

    flowdata = get_indicators_from_rapidpro_results(
        request_json, INDICATORS, report_type)

    def get_year_month_quarter(dtime_obj):
        current_quarter = int(round((dtime_obj.month - 1) / 3 + 1))
        year = dtime_obj.year
        month = '{0}-{1:02}'.format(year, dtime_obj.month)
        qt_str = '{0}Q{1}'.format(year, current_quarter)
        return year, month, qt_str

    year, month, quarter = get_year_month_quarter(datetime.datetime.now())

    res = db.query(
        "SELECT id FROM fcapp_flow_data WHERE "
        "district = $district AND facilityuid = $facilityuid AND msisdn=$msisdn AND report_type = $report_type "
        "AND values->>'hh_number' = $hh_number::text AND quarter=$quarter", {
            'district': allDistrictsByName.get(district, 0),
            'facilityuid': facilityuid,
            'msisdn': msisdn,
            'report_type': report_type,
            'hh_number': flowdata.get('hh_number', ''),
            'quarter': quarter
        })
    if res:
        rpt_id = res[0]['id']
        db.query("UPDATE fcapp_flow_data SET values=$values, updated= NOW() WHERE id = $id", {
            'id': rpt_id, 'values': psycopg2.extras.Json(flowdata, dumps=simplejson.dumps)})
    else:
        db.query(
            "INSERT INTO fcapp_flow_data (msisdn, district, facility, facilityuid, subcounty, "
            "village, report_type, values, year, quarter, month) "
            "VALUES($msisdn, $district, $facility, $facilityuid, $subcounty, $village, "
            "$report_type, $values, $year, $quarter, $month) ",
            {
                'msisdn': msisdn, 'district': allDistrictsByName.get(district, 0),
                'facility': facility, 'facilityuid': facilityuid, 'subcounty': subcounty,
                'village': village, 'report_type': report_type,
                'values': psycopg2.extras.Json(flowdata, dumps=simplejson.dumps),
                'year': year, 'quarter': quarter, 'month': month})
    print(flowdata)
